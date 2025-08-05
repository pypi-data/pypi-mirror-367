from __future__ import annotations

import os
from typing import TYPE_CHECKING, Callable, Mapping, Sequence, TextIO

from zut import Column
from zut.csv import ExaminedCsvFile, examine_csv_file
from zut.db import Db, DbObj, Upserted
from zut.polyfills.stdlib import cached_property
from zut.slugs import slugify

if TYPE_CHECKING:
    from typing import Literal
    from django.db.models import Model


class LoadOperation:
    # From init parameters

    file: str|os.PathLike|TextIO

    table: DbObj
    """ Destination table. If not set, the destination table will be a newly created temporary table. """

    create_table: bool
    """ Indicate whether the destionation table must be created. """

    headers: dict[str,Column]
    """ Headers in the source CSV file, associated to columns in the destination table (its name, and the SQL type that will be used in case of creation of the destination table, or for conversion of values). """

    key: Sequence[str]
    """ Column(s) used to reconciliate existing records (will be updated). Set to `[]` for insert only. """


    # During init analyzis
    
    examined_src: ExaminedCsvFile

    skip_columns: bool
    """ If True, at least one column of the source CSV file is skipped. """



    def __init__(self, db: Db,
                       file: str|os.PathLike|TextIO, table: str|tuple|type|DbObj|None = None, headers: Sequence[str|Column|Literal['*']]|Mapping[str,str|type|Column|Literal['*']]|None = None, *,
                       key: str|Sequence[str]|None = None, encoding='utf-8', create_table: bool|None = None, slugify_columns: Callable[[str],str]|bool = False):
        raise NotImplementedError() #FIXME: ROADMAP

        self.db = db

        # Input
        self.file = file
        self.encoding = encoding
        self.examined_src = examine_csv_file(self.file, encoding=encoding)

        # Table
        if table is None:
            self.table = self.db.get_random_table_name('tmp_load_')
            if not (self.create_table is None or self.create_table is True):
                raise ValueError(f"Invalid create_table={self.create_table} with a newly created temp table")
            self.create_table = True
        else:
            self.table = self.db.parse_obj(table)

            if create_table is None:
                create_table = not self.db.table_exists(table)
            self.create_table = create_table

        # Columns
        if slugify_columns is True:
            slugify_columns = slugify
        elif not slugify_columns:
            slugify_columns = lambda name: name

        if not headers:
            self.headers = {column: Column(slugify_columns(column)) for column in self.examined_src.headers}
            self.skip_columns = False
        else:
            skip_columns = None
            if isinstance(headers, Sequence):
                headers = {column.name if isinstance(column, Column) else column: column for column in headers}

            if not isinstance(headers, Mapping):
                raise TypeError(f"columns: {type(headers).__name__}")
        
            mapping: list[tuple[str, Column]] = []
            asterisk_pos = None
            explicit_src_columns = []
            missing_src_columns = []
            for pos, (src_name, column) in enumerate(headers.items()):
                if isinstance(column, str):
                    if column == '*':
                        if asterisk_pos is not None:
                            raise ValueError("Parameter 'columns' cannot have several '*'")
                        asterisk_pos = pos
                        break
                    column = Column(slugify_columns(column))
                elif isinstance(column, type):
                    column = Column(slugify_columns(src_name), type=column)
                else:
                    column.name = slugify_columns(column.name)

                if src_name in self.examined_src.headers:
                    explicit_src_columns.append(src_name)
                else:
                    missing_src_columns.append(src_name)

                mapping.append((src_name, column))

            if missing_src_columns:
                raise ValueError(f"Column not found in source CSV file: {', '.join(missing_src_columns)}")
        
            self.headers = {}
            for pos, (src_name, column) in enumerate(mapping):
                if pos == asterisk_pos:
                    skip_columns = False
                    for column in self.examined_src.headers:
                        if not column in explicit_src_columns:
                            self.headers[column] = Column(column)
                else:
                    self.headers[src_name] = column

            if skip_columns is None:
                skip_columns = any(src_name for src_name in self.examined_src.headers if src_name not in self.headers)

            self.skip_columns = skip_columns
        
        # Upsert key
        if not key:
            self.key = []
        elif isinstance(key, str):
            self.key = [key]
        else:
            self.key = key

        if self.create_table:
            self.key = [] # no need to upsert: the table will have just been created


    @cached_property
    def src_headers(self):
        return list(self.headers.keys())


    @cached_property
    def dst_headers(self):
        return list(column.name for column in self.headers.values())


    def run(self) -> Upserted:
        # Determine target columns and forein keys
        target_columns, target_pk, fk_reconciliate_columns = self._analyze_input_columns() #FIXME
        foreign_keys = self.db.get_reversed_foreign_keys(self.dst_headers, self.table)

        # Create target table if necessary
        updated_at_column: str|bool|None = None
        if self.create_table:
            if self.table.temp:
                self.db.create_table(self.table, target_columns, primary_key=True)
                updated_at_column = False
            else:
                self.db.create_table(self.table, target_columns, primary_key=True, inserted_at_column=True, updated_at_column=True)
                updated_at_column = True

        # Create intermediate load table if necessary
        if self.key or foreign_keys:
            intermediate_table = self.db.parse_obj(('temp', f'tmp_intermediate_{token_hex(8)}'))
            load_columns = {**target_columns, **fk_reconciliate_columns}
            if self.key and target_pk:
                load_columns['_existing_dst_pk'] = self.db.get_sql_type(target_pk)
            self.db.create_table(intermediate_table, columns=load_columns, primary_key=True)
        else:
            intermediate_table = None

        # Actual load, and merge if necessary
        try:
            #FIXME with open(file, 'r', encoding=encoding, newline='') if isinstance(file, (str,os.PathLike)) else nullcontext(file) as fp:
            total_count = self.db._actual_load_csv(self.file, intermediate_table or self.table, self.src_headers, self.examined_src.delimiter, self.examined_src.newline)

            if intermediate_table:
                from zut.db.operations.merge import MergeOperation
                merge_op = MergeOperation(self.db, intermediate_table, self.table, [column for column in target_columns], key=self.key, foreign_keys=foreign_keys)
                merge_op.set_shortcuts(updated_at_column=updated_at_column)
                merge_result = merge_op.run()
                inserted_count = merge_result.inserted_count
                updated_count = merge_result.updated_count
            else:
                inserted_count = total_count
                updated_count = 0

        finally:
            if intermediate_table:
                self.db.execute(f"DROP TABLE {intermediate_table.escaped}")

        return Upserted(inserted_count, updated_count, self.table, self.src_headers)
