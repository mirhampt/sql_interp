from esc_types import Esc, ListEsc, DictEsc

class UnknownTypeError(Exception): pass

class SQLInterp(object):
    """
    The main sql_interp object.
    """
    TYPE_MAP = { 
        list: ListEsc,
        tuple: ListEsc,
        dict: DictEsc,
    }

    def __init__(self):
        pass

    def interp(self, *args):
        """
        This method takes a list of SQL snippets and returns a SQL statement and
        a list of bind variables to be passed to the DB API's execute method.
        """
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
        """
        Returns the given object in the appropriate wrapper class from esc_types.py.

        In most cases, you will not need to call this directly.  However, if you are
        passing a string to the interp method that should be used as an SQL bind value
        and not raw SQL, you must pass it to this method to avoid a SQL injection
        vulnerability.  For example:

        >>> sqli = SQLInterp()
        >>> first_name = 'John'

        The following is wrong!  This could lead to a SQL injection attack.

        >>> sqli.interp("SELECT * FROM table WHERE first_name =", first_name)
        ('SELECT * FROM table WHERE first_name = John', ())

        This is the correct way.

        >>> sqli.interp("SELECT * FROM table WHERE first_name =", sqli.esc(first_name))
        ('SELECT * FROM table WHERE first_name = ?', ('John',))
        """
        if type(val) in self.TYPE_MAP:
            return self.TYPE_MAP[type(val)](val)
        else:
            return Esc(val)
