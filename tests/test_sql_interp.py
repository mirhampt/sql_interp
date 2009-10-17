from nose.tools import eq_, ok_, raises
from sql_interp import esc, sql_interp, UnknownTypeError
from esc_types import Esc, ListEsc, DictEsc

### Test esc() function.

def test_esc_int():
    obj = esc(1)
    eq_(type(obj), Esc)

def test_esc_str():
    obj = esc('')
    eq_(type(obj), Esc)

def test_esc_dict():
    obj = esc({})
    eq_(type(obj), DictEsc)

def test_esc_list():
    obj = esc([])
    eq_(type(obj), ListEsc)

def test_esc_tuple():
    # Tuples are treated identically to lists.
    obj = esc((1,))
    eq_(type(obj), ListEsc)

### Test sql_interp() function.

def test_sql_interp_no_whitespace():
    # Whitespace should be added between arguments.
    sql, bind = sql_interp("SELECT", "*", "FROM table")
    eq_(sql, "SELECT * FROM table")
    eq_(bind, ())

    cols = ['one', 'two', 'three']
    sql, bind = sql_interp("SELECT", cols, "FROM table")
    eq_(sql, "SELECT (?, ?, ?) FROM table")
    eq_(bind, ('one', 'two', 'three'))

def test_sql_interp_extra_whitespace():
    # Excess whitespace is fine.
    sql, bind = sql_interp("SELECT ", " *", "   FROM table")
    eq_(sql, "SELECT  *    FROM table")
    eq_(bind, ())

def test_sql_interp_dict():
    where = { 'first_name': 'John', 'last_name': 'Doe' }
    sql, bind = sql_interp("SELECT * FROM users WHERE", where)
    eq_(sql, "SELECT * FROM users WHERE first_name = ? AND last_name = ?")
    eq_(bind, ('John', 'Doe'))

    where = { 'first_name': ['John', 'Jane'], 'last_name': 'Doe' }
    sql, bind = sql_interp("SELECT * FROM users WHERE", where)
    eq_(sql, "SELECT * FROM users WHERE first_name IN (?, ?) AND last_name = ?")
    eq_(bind, ('John', 'Jane', 'Doe'))

def test_sql_interp_dict_none():
    where = { 'first_name': None, 'last_name': 'Doe' }
    sql, bind = sql_interp("SELECT * FROM users WHERE", where)
    eq_(sql, "SELECT * FROM users WHERE first_name IS NULL AND last_name = ?")
    eq_(bind, ('Doe',))

def test_sql_interp_tuple():
    # Tuples are treated identically to lists.
    cols = ('one', 'two', 'three')
    sql, bind = sql_interp("SELECT", cols, "FROM table")
    eq_(sql, "SELECT (?, ?, ?) FROM table")
    eq_(bind, ('one', 'two', 'three'))

def test_sql_interp_string():
    full_name = 'John Doe'
    sql, bind = sql_interp("SELECT * FROM table WHERE full_name =", esc(full_name))
    eq_(sql, "SELECT * FROM table WHERE full_name = ?")
    eq_(bind, ('John Doe',))
