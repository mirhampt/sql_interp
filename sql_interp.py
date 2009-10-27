from esc_types import Esc, ListEsc, DictEsc

class UnknownTypeError(Exception): pass

class SQLInterp(object):
    TYPE_MAP = { 
        list: ListEsc,
        tuple: ListEsc,
        dict: DictEsc,
    }

    def __init__(self):
        pass

    def interp(self, *args):
        sql = ""
        bind = ()

        def _append_sql(sql, part):
            "Handle whitespace when appending properly."
            if len(sql) == 0:
                return part
            elif sql[-1] == ' ':
                return sql + part
            else:
                return sql + ' ' + part

        for arg in args:
            if type(arg) is str:
                # Strings are treated as raw SQL.
                sql = _append_sql(sql, arg)
            elif isinstance(arg, Esc):
                # If this is an instance of Esc, ask the object
                # how to represent the data given the context.
                arg_sql, arg_bind = arg.to_string(sql)
                sql = _append_sql(sql, arg_sql)
                bind += arg_bind
            else:
                # Any argument given that is not a string or Esc
                # is an error.
                arg_sql, arg_bind = self.esc(arg).to_string(sql)
                sql = _append_sql(sql, arg_sql)
                bind += arg_bind

        return (sql, bind)

    def esc(self, val):
        if type(val) in self.TYPE_MAP:
            return self.TYPE_MAP[type(val)](val)
        else:
            return Esc(val)
