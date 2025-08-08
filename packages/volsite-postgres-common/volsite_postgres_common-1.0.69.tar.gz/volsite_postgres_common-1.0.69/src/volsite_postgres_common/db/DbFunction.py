class DbFunction:
    def __init__(self, schema: str, id: str, name: str, is_hex_id: bool = True):
        self.qualified_name = f"{schema}.{name}"
        self.schema = schema
        self.name = name
        self.id = id
        if is_hex_id:
            assert DbFunction.is_hex_string(id), f"[{id}] is not hex!"

    @staticmethod
    def is_hex_string(s: str):
        try:
            int(s, 16)
            return True
        except ValueError:
            return False

    @staticmethod
    def build_qualified_function_name_id_dict(function_group_class_list):
        ids = {}
        # fs = [ScF.Game]
        for f_class in function_group_class_list:
            for name, value in vars(f_class).items():
                if isinstance(value, DbFunction):
                    f: DbFunction = value
                    ids[f.qualified_name] = f.id
        return ids