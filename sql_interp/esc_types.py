"""
Contains Esc class and its subclasses.

To make SQLInterp play nice with your custom objects, you may wish to subclass
the Esc class.
"""
import re


__all__ = ['Esc', 'ListEsc', 'DictEsc', 'UnknownContextError']


# Regular expressions to determine context.
# Borrowed directly from SQL::Interp.
RE_FLAGS = re.S | re.I
NOT_IN_RE = re.compile(r'\b(?:NOT\s+)?IN\s*$', RE_FLAGS)
SET_UPDATE_RE = re.compile(r'\b(?:ON\s+DUPLICATE\s+KEY\s+UPDATE|SET)\s*$', RE_FLAGS)
INSERT_INTO_RE = re.compile(r'\bINSERT[\w\s]*\sINTO\s*[a-zA-Z_][a-zA-Z0-9_\$\.]*\s*$', RE_FLAGS)
FROM_JOIN_RE = re.compile(r'(?:\bFROM|JOIN)\s*$', RE_FLAGS)


class UnknownContextError(Exception):
    """
    Raised when a value does not know how to insert itself into a given
    context.
    """
    pass


class Esc(object):
    """
    An Esc object knows how to display its value in different SQL contexts.

    Most Python types will be handled by a bundled subclass of Esc, but you may
    wish to subclass Esc to handle a custom object.

    To handle a custom object you will need to create a subclass of Esc and override
    the following methods to return a SQL snippet and a tuple of bind values for
    the specified context:

    * ``in_ctxt``
    * ``set_update_ctxt``
    * ``insert_into_ctxt``
    * ``from_join_ctxt``
    * ``default_ctxt``
    """
    def __init__(self, val):
        self.val = val

    def to_string(self, sql):
        """
        Returns a snippet of sql and a tuple of bind values.

        Params::
            sql     The SQL that precedes the point where the value is to
                    be interpolated.
        """
        if NOT_IN_RE.search(sql):
            return self.in_ctxt()
        elif SET_UPDATE_RE.search(sql):
            return self.set_update_ctxt()
        elif INSERT_INTO_RE.search(sql):
            return self.insert_into_ctxt()
        elif FROM_JOIN_RE.search(sql):
            return self.from_join_ctxt()
        else:
            return self.default_ctxt()

    def in_ctxt(self):
        "Handle the SQL 'IN/NOT IN' context."
        raise UnknownContextError("IN context not implemented for this type")

    def set_update_ctxt(self):
        "Handle the SQL 'SET/UPDATE' context."
        raise UnknownContextError("SET/UPDATE context not implemented for this type")

    def insert_into_ctxt(self):
        "Handle the SQL 'INSERT INTO' context."
        raise UnknownContextError("INSERT context not implemented for this type")

    def from_join_ctxt(self):
        "Handle the SQL 'FROM/JOIN' context."
        raise UnknownContextError("FROM/JOIN context not implemented for this type")

    def default_ctxt(self):
        """
        If we don't know the context, just return a single placeholder and
        bind value.
        """
        if type(self.val) is str:
            bind = (self.val,)
        else:
            try:
                bind = tuple(self.val)
            except TypeError:
                bind = (self.val,)

        return '?', bind


class ListEsc(Esc):
    """
    Subclass of ``Esc`` to handle lists and tuples.
    """
    def __init__(self, val):
        self.val = tuple(val)

    def in_ctxt(self):
        return self.default_ctxt()

    def insert_into_ctxt(self):
        sql = 'VALUES (' + ', '.join(['?' for _ in self.val]) + ')'
        return sql, self.val

    def default_ctxt(self):
        sql = '(' + ', '.join(['?' for _ in self.val]) + ')'
        return sql, self.val


class DictEsc(Esc):
    """
    Subclass of ``Esc`` to handle dictionaries.
    """
    def __init__(self, val):
        self.val = val

    def set_update_ctxt(self):
        sorted_keys = sorted(self.val.keys())

        sql = " = ?, ".join(sorted_keys) + " = ?"
        bind = [self.val[key] for key in sorted_keys]

        return sql, tuple(bind)

    def insert_into_ctxt(self):
        sorted_keys = sorted(self.val.keys())

        sql = "(" + ", ".join(sorted_keys) + ") VALUES (" \
            + ", ".join('?' for _ in sorted_keys) + ")"
        bind = [self.val[key] for key in sorted_keys]

        return sql, tuple(bind)

    def default_ctxt(self):
        sorted_keys = sorted(self.val.keys())

        sql_bits = []
        bind = []

        for key in sorted_keys:
            val = self.val[key]
            if val is None:
                sql_bits.append(key + " IS NULL")
            elif type(val) is list:
                # i.e. key IN (?, ?)
                val_sql, val_bind = ListEsc(val).default_ctxt()
                sql_bits.append(key + " IN " + val_sql)
                for v in val_bind:
                    bind.append(v)
            else:
                sql_bits.append(key + " = ?")
                bind.append(val)

        sql = " AND ".join(sql_bits)

        return sql, tuple(bind)
