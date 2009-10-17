from esc_types import Esc, ListEsc, DictEsc

TYPE_MAP = { 
    list: ListEsc,
    tuple: ListEsc,
    dict: DictEsc,
}

class UnknownTypeError(Exception): pass

def sql_interp(*args):
    """
    Interpolate python variables into SQL based upon context.

    Indirect port of Perl's SQL::Interp.

    Example:

    >>> item = { 'first_name': 'John', 'last_name': 'Doe' }
    >>> sql_interp("INSERT INTO table", item)
    ('INSERT INTO table (first_name, last_name) VALUES (?, ?)', ('John', 'Doe'))
    >>> sql_interp("UPDATE table SET", item, "WHERE y <>", 2)
    ('UPDATE table SET first_name = ?, last_name = ? WHERE y <> ?', ('John', 'Doe', 2))
    >>> sql_interp("DELETE FROM table WHERE y =", 2)
    ('DELETE FROM table WHERE y = ?', (2,))
    
    # The following two examples produce the same result.
    >>> sql_interp("SELECT * FROM table WHERE x =", 3, "AND y IN", [1,2,3])
    ('SELECT * FROM table WHERE x = ? AND y IN (?, ?, ?)', (3, 1, 2, 3))
    >>> sql_interp("SELECT * FROM table WHERE", { 'x': 3, 'y': [1, 2, 3] })
    ('SELECT * FROM table WHERE x = ? AND y IN (?, ?, ?)', (3, 1, 2, 3))

    CAUTION: If the value to be interpolated is a string, you must pass it to the esc()
    function first or it will be treated as raw SQL.  Forgetting to do this could pose
    a security risk.

    >>> first_name = 'John'

    # The following is wrong!  This could lead to a SQL injection attack!
    >>> sql_interp("SELECT * FROM table WHERE first_name =", first_name)
    ('SELECT * FROM table WHERE first_name = John', ())

    # This is the correct way.
    >>> sql_interp("SELECT * FROM table WHERE first_name =", esc(first_name))
    ('SELECT * FROM table WHERE first_name = ?', ('John',))
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
            arg_sql, arg_bind = esc(arg).to_string(sql)
            sql = _append_sql(sql, arg_sql)
            bind += arg_bind

    return (sql, bind)

def esc(val):
    """
    """
    if type(val) in TYPE_MAP:
        return TYPE_MAP[type(val)](val)
    else:
        return Esc(val)
