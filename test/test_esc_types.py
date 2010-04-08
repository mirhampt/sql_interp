import unittest
from sql_interp.esc_types import Esc, ListEsc, DictEsc, UnknownContextError


class ListEscTest(unittest.TestCase):
    """
    Unit tests for ``ListEsc`` class.
    """
    def setUp(self):
        "Create a test ``ListEsc`` object."
        self.list_esc = ListEsc(['one', 'two', 'three'])

    def test_in_ctxt(self):
        "Test IN context."
        sql, bind = self.list_esc.in_ctxt()
        self.assertEquals(sql, '(?, ?, ?)')
        self.assertEquals(bind, ('one', 'two', 'three'))

    def test_set_update_ctxt(self):
        "SET/UPDATE context is not implemented for lists."
        self.assertRaises(UnknownContextError, self.list_esc.set_update_ctxt)

    def test_insert_into_ctxt(self):
        "Test INSERT INTO context."
        sql, bind = self.list_esc.insert_into_ctxt()
        self.assertEquals(sql, 'VALUES (?, ?, ?)')
        self.assertEquals(bind, ('one', 'two', 'three'))

    def test_from_join_ctxt(self):
        "FROM/JOIN context is not implemented for lists."
        self.assertRaises(UnknownContextError, self.list_esc.from_join_ctxt)

    def test_default_ctxt(self):
        "Test default context."
        sql, bind = self.list_esc.default_ctxt()
        self.assertEquals(sql, '(?, ?, ?)')
        self.assertEquals(bind, ('one', 'two', 'three'))


class DictEscTest(unittest.TestCase):
    """
    Unit tests for ``DictEsc`` class.
    """
    def setUp(self):
        "Create a test ``DictEsc`` object."
        self.dict_esc = DictEsc({'one' : 1, 'two' : 2, 'three' : 3})

    def test_in_ctxt(self):
        "IN context is not implemented for dicts."
        self.assertRaises(UnknownContextError, self.dict_esc.in_ctxt)

    def test_set_update_ctxt(self):
        "Test SET/UPDATE context."
        sql, bind = self.dict_esc.set_update_ctxt()
        self.assertEquals(sql, 'one = ?, three = ?, two = ?')
        self.assertEquals(bind, (1, 3, 2))

    def test_insert_into_ctxt(self):
        "Test INSERT INTO context."
        sql, bind = self.dict_esc.insert_into_ctxt()
        self.assertEquals(sql, '(one, three, two) VALUES (?, ?, ?)')
        self.assertEquals(bind, (1, 3, 2))

    def test_from_join_ctxt(self):
        "FROM/JOIN context is not implemented for lists."
        self.assertRaises(UnknownContextError, self.dict_esc.from_join_ctxt)

    def test_default_ctxt(self):
        "Test default context."
        sql, bind = self.dict_esc.default_ctxt()
        self.assertEquals(sql, 'one = ? AND three = ? AND two = ?')
        self.assertEquals(bind, (1, 3, 2))


if __name__ == "__main__":
    unittest.main()
