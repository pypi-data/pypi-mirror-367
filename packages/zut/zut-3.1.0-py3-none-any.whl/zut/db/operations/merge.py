from __future__ import annotations

from typing import TYPE_CHECKING, Mapping, Sequence

from zut import Column
from zut.db import Db, DbObj, Upserted, ForeignKey

if TYPE_CHECKING:
    from typing import Literal

class MergeOperation:
    src_table: DbObj
    """ Source table """

    dst_table: DbObj
    """ Destination table """

    columns: Mapping[str,str]
    """ Association of source column names with destination column names. """

    key: Sequence[str]
    """ Column(s) used to reconciliate existing records (will be updated). Set to `[]` for insert only. """

    # Will either be set through `_set_shortcuts` (optimization) or calculated at the beginning `run`
    updated_at_column: str|Literal[False]|None = None

    def __init__(self,
                 db: Db,
                 src_table: str|tuple|type|DbObj,
                 dst_table: str|tuple|type|DbObj,
                 columns: Sequence[str]|Mapping[str,str]|None = None, *,
                 key: str|Sequence[str]|None = None,
                 foreign_keys: Sequence[ForeignKey]|None = None,
                 # NOTE: below are optimizations (they may be calculated within `merge_tables` but we may also pass them to avoid recalculation)
                 #dst_pk: Column|None = None, 
                 ):
        raise NotImplementedError() #FIXME: ROADMAP
    
        self.db = db

        self.src_table = self.db.parse_obj(src_table)
        self.dst_table = self.db.parse_obj(dst_table)

        if not key:
            self.key = []
        elif isinstance(key, str):
            self.key = [key]
        else:
            self.key = key


    def _set_shortcuts(self, *, updated_at_column: bool):
        if updated_at_column is True:
            self.updated_at_column = self.db.updated_at_default_column
        else:
            self.updated_at_column = updated_at_column


    def run(self) -> Upserted:
        src_columns = self.db.get_columns(src_table)

        if columns is None:
            columns = [c.name for c in src_columns]

        src_pk_columns = [column for column in src_columns if column.primary_key]
        if len(src_pk_columns) == 0:
            raise ValueError(f"Source table {src_table} does not have a pk")
        if len(src_pk_columns) >= 2:
            raise ValueError(f"Source table {src_table} pk has several columns: {', '.join(c.name for c in src_pk_columns)}")
        src_pk = src_pk_columns[0]

        src_existing_dst_pk: Column|None = None
        if key: # NOTE: no need to determine whereas there is an `src_existing_dst_pk` column if there is no key, because there would be no UPDATE anyway
            for column in src_columns:
                if column.name == '_existing_dst_pk':
                    src_existing_dst_pk = column
                    break
            if not src_existing_dst_pk:
                raise NotImplementedError() # FIXME / we would have to create 

        if not isinstance(columns, list):
            columns = [column for column in columns]

        dst_columns = self.get_columns(dst_table)

        dst_pk_columns = [column for column in dst_columns if column.is_primary]
        if len(dst_pk_columns) == 0:
            raise ValueError(f"Destination table {dst_table} does not have a pk")
        if len(dst_pk_columns) >= 2:
            raise ValueError(f"Destination table {dst_table} pk has several columns: {', '.join(c.name for c in dst_pk_columns)}")
        dst_pk = dst_pk_columns[0]

        if self.updated_at_column is None:
            if not self.key: # NOTE: no need to determine whereas there is an `updated_at` column if there is no key, because there would be no UPDATE anyway
                if any(c.name == self.db.updated_at_default_column for c in dst_columns):
                    self.updated_at_column = self.db.updated_at_default_column
        elif self.updated_at_column is False:
            self.updated_at_column = None

        return self.db._actual_merge_tables(src_table, dst_table, columns, key=self.key,
                                         updated_at_column=self.updated_at_column, src_pk=src_pk, dst_pk=dst_pk)
