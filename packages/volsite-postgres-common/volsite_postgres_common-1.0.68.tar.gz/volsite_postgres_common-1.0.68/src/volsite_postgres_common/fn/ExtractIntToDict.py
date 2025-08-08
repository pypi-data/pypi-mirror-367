from typing import Final

from volworld_common.api.CA import CA

from volsite_postgres_common.db.CFn import CFn

from volsite_postgres_common.fn.function import Arg, AJsonPlPgSqlFunction
from volsite_postgres_common.db.BFn import BFn
from volsite_postgres_common.db.FnT import FnT


class ExtractIntToDict(AJsonPlPgSqlFunction):
    def name(self) -> str:
        return CFn.extract_int_to_dict

    _data: Final[str] = "_data"
    _ext: Final[str] = "_ext"
    _key: Final[str] = "_key"
    _value: Final[str] = "_value"

    def declare(self) -> list:
        return [
            Arg(self._data, FnT.JSONB),
            Arg(self._ext, FnT.TEXT),
            Arg(self._key, FnT.TEXT),
            Arg(self._value, FnT.JSONB),
        ]

    '''
    A.Data :{
         key: {
            JSON_KEY: value
         }
    }
    A.Key
    '''
    def body(self) -> str:
        return (
            f" {self._data} := ({Arg.input}->>'{CA.Data}')::{FnT.JSONB};"
            f" {self._ext} := ({Arg.input}->>'{CA.Key}')::{FnT.TEXT};"
            f" {Arg.result} := '{{}}';"
            f""
            # f"  RAISE NOTICE 'self._data = %', {self._data}; "
            # f"  RAISE NOTICE 'self._ext = %', {self._ext}; "
            f""
            f" FOR {self._key}, {self._value} IN"
            f"   SELECT * FROM {BFn.jsonb_each}({self._data})"
            f" LOOP"
            # f"  RAISE NOTICE 'self._key = %', {self._key}; "
            # f"  RAISE NOTICE 'self._value = %', {self._value}; "
            # f"  RAISE NOTICE 'self._ext = %', {self._value}->>{self._ext}; "
            f""
            f"   IF NOT ({self._value} ? {self._ext}) THEN"
            f"      RAISE EXCEPTION 'Extract key \"%\" not found in JSON object \"%\"', {self._ext}, {self._key};"
            f"   END IF;"
            f"   "
            f"   {Arg.result} := {Arg.result} || {BFn.jsonb_build_object}({self._key}, ({self._value}->>{self._ext})::{FnT.INT});"
            f" END LOOP;"
        )
