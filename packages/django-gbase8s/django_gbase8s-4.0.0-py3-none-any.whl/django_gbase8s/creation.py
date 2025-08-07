from django.db.backends.base.creation import BaseDatabaseCreation

class DatabaseCreation(BaseDatabaseCreation):
    
    def sql_table_creation_suffix(self):
        """
        SQL to append to the end of the test table creation statements.
        """
        return "WITH LOG"

    def _destroy_test_db(self, test_database_name, verbosity):
        with self._nodb_cursor() as cursor:
            cursor.execute("DROP DATABASE %s"
                           % self.connection.ops.quote_name(test_database_name))