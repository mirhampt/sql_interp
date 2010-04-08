import unittest
from sql_interp import SQLInterp
from sql_interp.esc_types import Esc, ListEsc, DictEsc


class SQLInterpEscTest(unittest.TestCase):
    """
    Unit tests for ``SQLInterp``'s ``esc`` method.
    """
    def setUp(self):
        "Create a SQLInterp instance for testing."
        self.sqli = SQLInterp()

    def test_esc_int(self):
        "An integer should be wrapped by an ``Esc`` instance."
        obj = self.sqli.esc(1)
        self.assertEquals(type(obj), Esc)

    def test_esc_str(self):
        "A string should be wrapped by an ``Esc`` instance."
        obj = self.sqli.esc('')
        self.assertEquals(type(obj), Esc)

    def test_esc_dict(self):
        "A dictionary should be wrapped by a ``DictEsc`` instance."
        obj = self.sqli.esc({})
        self.assertEquals(type(obj), DictEsc)

    def test_esc_list(self):
        "A list should be wrapped by a ``ListEsc`` instance."
        obj = self.sqli.esc([])
        self.assertEquals(type(obj), ListEsc)

    def test_esc_tuple(self):
        "A tuple should be wrapped by a ``ListEsc`` instance."
        # Tuples are treated identically to lists.
        obj = self.sqli.esc((1,))
        self.assertEquals(type(obj), ListEsc)


class SQLInterpCustomTypesTest(unittest.TestCase):
    """
    Unit tests for ``SQLInterp``'s custom types features.
    """
    def setUp(self):
        """
        Create an object and a corresponding subclass of ``Esc`` for testing.
        """
        class MyClass(object): pass
        class MyClassEsc(Esc): pass

        self.custom_cls = MyClass
        self.custom_cls_esc = MyClassEsc

    def test_add_types_custom(self):
        """
        Test ``SQLInterp``'s ``add_types`` method.
        """
        sqli = SQLInterp()

        sqli.add_types({ self.custom_cls: self.custom_cls_esc })
        
        obj = sqli.esc(self.custom_cls())
        self.assertEquals(type(obj), self.custom_cls_esc)

    def test_add_types_custom_constructor(self):
        """
        Test ``SQLInterp``'s ability to add custom types via its constructor.
        """
        sqli = SQLInterp({ self.custom_cls: self.custom_cls_esc })
        
        obj = sqli.esc(self.custom_cls())
        self.assertEquals(type(obj), self.custom_cls_esc)


class SQLInterpTest(unittest.TestCase):
    """
    Unit tests for ``SQLInterp``'s ``interp`` method.
    """
    def setUp(self):
        "Create custom ``SQLInterp`` instance for testing."
        self.sqli = SQLInterp()

    def test_sql_interp_no_whitespace(self):
        "Whitespace should be added between arguments."
        sql, bind = self.sqli.interp("SELECT", "*", "FROM table")
        self.assertEquals(sql, "SELECT * FROM table")
        self.assertEquals(bind, ())

        cols = ['one', 'two', 'three']
        sql, bind = self.sqli.interp("SELECT", cols, "FROM table")
        self.assertEquals(sql, "SELECT (?, ?, ?) FROM table")
        self.assertEquals(bind, ('one', 'two', 'three'))

    def test_sql_interp_extra_whitespace(self):
        "Excess whitespace is fine."
        sql, bind = self.sqli.interp("SELECT ", " *", "   FROM table")
        self.assertEquals(sql, "SELECT  *    FROM table")
        self.assertEquals(bind, ())

    def test_sql_interp_dict(self):
        "Test interpolating a dictionary."
        where = { 'first_name': 'John', 'last_name': 'Doe' }
        sql, bind = self.sqli.interp("SELECT * FROM users WHERE", where)
        self.assertEquals(sql, "SELECT * FROM users WHERE first_name = ? AND last_name = ?")
        self.assertEquals(bind, ('John', 'Doe'))

        where = { 'first_name': ['John', 'Jane'], 'last_name': 'Doe' }
        sql, bind = self.sqli.interp("SELECT * FROM users WHERE", where)
        self.assertEquals(sql, "SELECT * FROM users WHERE first_name IN (?, ?) AND last_name = ?")
        self.assertEquals(bind, ('John', 'Jane', 'Doe'))

    def test_sql_interp_dict_none(self):
        "Test interpolating a dictionary containing a ``None`` value."
        where = { 'first_name': None, 'last_name': 'Doe' }
        sql, bind = self.sqli.interp("SELECT * FROM users WHERE", where)
        self.assertEquals(sql, "SELECT * FROM users WHERE first_name IS NULL AND last_name = ?")
        self.assertEquals(bind, ('Doe',))

    def test_sql_interp_tuple(self):
        "Test interpolating a tuple."
        # Tuples are treated identically to lists.
        cols = ('one', 'two', 'three')
        sql, bind = self.sqli.interp("SELECT", cols, "FROM table")
        self.assertEquals(sql, "SELECT (?, ?, ?) FROM table")
        self.assertEquals(bind, ('one', 'two', 'three'))

    def test_sql_interp_string(self):
        "Test interpolating a string."
        full_name = 'John Doe'
        sql, bind = self.sqli.interp("SELECT * FROM table WHERE full_name =",
            self.sqli.esc(full_name))
        self.assertEquals(sql, "SELECT * FROM table WHERE full_name = ?")
        self.assertEquals(bind, ('John Doe',))


if __name__ == "__main__":
    unittest.main()
