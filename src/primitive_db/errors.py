class DatabaseError(Exception):
    pass


class TableAlreadyExists(DatabaseError):
    pass


class TableDoesntExist(DatabaseError):
    pass


class ColumnTypeError(DatabaseError):
    pass


class ParseArgumentsError(DatabaseError):
    pass
