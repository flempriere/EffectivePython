# db_connection.py
import __main__


class TestingDatabase:
    pass


class RealDatabase:
    pass


if __main__.TESTING:
    Database = TestingDatabase
else:
    Database = RealDatabase
