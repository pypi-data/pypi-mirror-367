import decimal
from contextlib import contextmanager
from collections.abc import Mapping

from django.core.exceptions import ImproperlyConfigured
from django.db.backends.base.base import BaseDatabaseWrapper
from django.db.backends.base.base import NO_DB_ALIAS
from django.utils.asyncio import async_unsafe
from django.utils.regex_helper import _lazy_re_compile

try:
    import gbase8sdb as Database
    Database.defaults.fetch_decimals = True
except ImportError as e:
    raise ImproperlyConfigured("Error loading gbase8sdb module: %s" % e)

from .client import DatabaseClient
from .creation import DatabaseCreation
from .features import DatabaseFeatures
from .introspection import DatabaseIntrospection
from .operations import DatabaseOperations
from .schema import DatabaseSchemaEditor
from .validation import DatabaseValidation
from .utils import dsn
from .utils import GBase8sParam


FORMAT_QMARK_REGEX = _lazy_re_compile(r"(?<!%)%s")


class CursorWrapper(object):
    def __init__(self, cursor):
        self.cursor = cursor

    def _format_params(self, params):
        if isinstance(params, (list, tuple)):
            return tuple(GBase8sParam(p) for p in params)
        elif isinstance(params, dict):
            return {k: GBase8sParam(v) for k, v in params.items()}
        else:
            raise TypeError("params must be tuple or dict")


    def _param_generator(self, gbase8sparams):
        if isinstance(gbase8sparams, (list, tuple)):
            return tuple(p.param for p in gbase8sparams)
        elif isinstance(gbase8sparams, dict):
            return {k: v.param for k, v in gbase8sparams.items()}
        else:
            raise TypeError("params must be tuple or dict")

    def _param_inputsize(self, gbase8sparams_list):
        if hasattr(gbase8sparams_list[0], 'keys'): # [{k: gbase8sparams}, {}...]
            sizes = {}
            for params in gbase8sparams_list:
                for k, value in params.items():
                    if value.input_size:
                        sizes[k] = value.input_size
        else:
            sizes = [None] * len(gbase8sparams_list[0])
            for params in gbase8sparams_list:
                for i, value in enumerate(params):
                    if value.input_size:
                        sizes[i] = value.input_size
            return sizes
        
    def _format_sql(self, sql, params):
        if not params:
            return FORMAT_QMARK_REGEX.sub("?", sql).replace("%%", "%")
        elif isinstance(params, (tuple, list)):
            sql = sql % tuple('?' * len(params))
        elif isinstance(params, Mapping):
            sql = sql % {name: ":{name}".format(name=name) for name in params}
        else:
            raise TypeError("params must be tuple or dict")
        return sql
    
    def execute(self, sql, params=None):
        if params is None:
            return self.cursor.execute(sql)
        sql = self._format_sql(sql, params)
        gbase8sparams = self._format_params(params)
        params = self._param_generator(gbase8sparams)
        input_sizes = self._param_inputsize([gbase8sparams])
        if isinstance(input_sizes, (list, tuple)):         
            self.cursor.setinputsizes(*input_sizes)
        elif isinstance(input_sizes, dict):
            self.cursor.setinputsizes(**input_sizes)
        cursor = self.cursor.execute(sql, params)
        return cursor

    def executemany(self, sql, params_list=()):
        if not params_list:
            return None
        params_list = list(params_list)
        sql = self._format_sql(sql, params_list[0])
        
        new_params_list = []
        gbase8sparams_list = []
        for params in params_list:            
            gbase8sparams = self._format_params(params)
            gbase8sparams_list.append(gbase8sparams)
            params = self._param_generator(gbase8sparams)
            new_params_list.append(params)
        input_sizes = self._param_inputsize(gbase8sparams_list)      
        if isinstance(input_sizes, (list, tuple)):
            self.cursor.setinputsizes(*input_sizes)
        elif isinstance(input_sizes, dict):
            self.cursor.setinputsizes(**input_sizes)
        return self.cursor.executemany(sql, new_params_list)
    
    @property
    def lastrowid(self):
        return self.cursor.lastrowid

    def __getattr__(self, attr):
        return getattr(self.cursor, attr)
    
    def __iter__(self):
        return iter(self.cursor)
    

class DatabaseWrapper(BaseDatabaseWrapper):
    vendor = 'gbase8s'
    display_name = "GBase 8s"
    Database = Database
    isolation_levels = [
            "DIRTY READ", 
            "COMMITTED READ LAST COMMITTED", 
            "COMMITTED READ", 
            "CURSOR STABILITY",
            "REPEATABLE READ",             
            ]
    _limited_data_types = ("clob", "nclob", "blob")
    data_types = {
        'AutoField': 'SERIAL',
        'SmallAutoField': 'SERIAL',
        'BigAutoField': 'BIGSERIAL',
        'BinaryField': 'BLOB',
        'BooleanField': 'NUMBER(1)',
        'CharField': 'VARCHAR(%(max_length)s)',
        'DateField': 'TIMESTAMP(0)',
        'DateTimeField': 'TIMESTAMP',
        'DecimalField': 'NUMBER(%(max_digits)s, %(decimal_places)s)',
        'DurationField': 'INTERVAL DAY(9) TO SECOND(5)',
        'FileField': 'VARCHAR(%(max_length)s)',
        'FilePathField': 'VARCHAR(%(max_length)s)',
        'FloatField': 'FLOAT',
        'IntegerField': 'INTEGER',
        "JSONField": 'VARCHAR(32765)',
        'BigIntegerField': 'BIGINT',
        'IPAddressField': 'VARCHAR(15)',
        'GenericIPAddressField': 'VARCHAR(39)',
        'OneToOneField': 'INTEGER',
        'PositiveIntegerField': 'INTEGER',
        'PositiveSmallIntegerField': 'INTEGER',
        "PositiveBigIntegerField": "BIGINT",
        'SlugField': 'VARCHAR(%(max_length)s)',
        'SmallIntegerField': 'INTEGER',
        'TextField': 'NCLOB',
        'TimeField': 'TIMESTAMP',
        "URLField": "VARCHAR(%(max_length)s)",
        'UUIDField': 'VARCHAR(32)',
    }
    data_type_check_constraints = {
        "BooleanField": "%(qn_column)s IN (0,1)",
        "JSONField": "%(qn_column)s IS JSON",
        "PositiveBigIntegerField": "%(qn_column)s >= 0",
        "PositiveIntegerField": "%(qn_column)s >= 0",
        "PositiveSmallIntegerField": "%(qn_column)s >= 0",
    }
    operators = {
        "exact": "= %s",
        "iexact": "= UPPER(%s)",
        "contains": "LIKE %s ESCAPE '\\'",
        "icontains": "LIKE UPPER(%s) ESCAPE '\\'",
        "gt": "> %s",
        "gte": ">= %s",
        "lt": "< %s",
        "lte": "<= %s",
        "startswith": "LIKE %s ESCAPE '\\'",
        "endswith": "LIKE %s ESCAPE '\\'",
        "istartswith": "LIKE UPPER(%s) ESCAPE '\\'",
        "iendswith": "LIKE UPPER(%s) ESCAPE '\\'",
    }
    pattern_esc = r"REPLACE(REPLACE(REPLACE({}, '\', '\\'), '%%', '\%%'), '_', '\_')"
    pattern_ops = {
        "contains": r"LIKE '%%' || {} || '%%' ESCAPE '\'",
        "icontains": r"LIKE '%%' || UPPER({}) || '%%' ESCAPE '\'",
        "startswith": r"LIKE {} || '%%' ESCAPE '\'",
        "istartswith": r"LIKE UPPER({}) || '%%' ESCAPE '\'",
        "endswith": r"LIKE '%%' || {} ESCAPE '\'",
        "iendswith": r"LIKE '%%' || UPPER({}) ESCAPE '\'",
    }
    client_class = DatabaseClient
    creation_class = DatabaseCreation
    features_class = DatabaseFeatures
    introspection_class = DatabaseIntrospection
    ops_class = DatabaseOperations
    SchemaEditorClass = DatabaseSchemaEditor
    validation_class = DatabaseValidation
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.isolation_level = 'COMMITTED READ LAST COMMITTED'
    
    def get_database_version(self):
        return (8, 8)
    
    def get_connection_params(self):
        conn_params = {
            "user": self.settings_dict["USER"],
            "password": self.settings_dict["PASSWORD"],
            "dsn": dsn(self.settings_dict)            
        }
        if 'ISOLATION_LEVEL' in self.settings_dict['OPTIONS']:
            if self.settings_dict['OPTIONS']['ISOLATION_LEVEL'].upper() in self.isolation_levels:
                self.isolation_level = self.settings_dict['OPTIONS']['ISOLATION_LEVEL']
            else:
                raise ImproperlyConfigured(f"Invalid isolation level, need {self.isolation_levels}")
            
        return conn_params
    
    @async_unsafe
    def get_new_connection(self, conn_params):
        conn = Database.connect(**conn_params)
        cursor = conn.cursor()
        cursor.execute("select 1 from sysprocedures where procname='django_isoyear_extract'")
        if not cursor.fetchone():
            cursor.execute("""
create or replace function django_isoyear_extract(d in timestamp)
return int as
	v_year int;
begin
	SELECT
	  CASE
		WHEN WEEKDAY(d) = 0 THEN YEAR(d -3 UNITS DAY)
		ELSE YEAR(d + (4 - WEEKDAY(d)) UNITS DAY)
	  END AS iso_year
	  INTO v_year
	FROM DUAL;
	return v_year;
end django_isoyear_extract;
                """)
        cursor.close()

        return conn
    
    def init_connection_state(self):
        # super().init_connection_state()
        if self.isolation_level:
            with self.cursor() as cursor:
                cursor.execute(f"SET ISOLATION TO {self.isolation_level}")
                
    def create_cursor(self, name=None):
        return CursorWrapper(self.connection.cursor())
    
    def _set_autocommit(self, autocommit):
        with self.wrap_database_errors:
            self.connection.autocommit = autocommit
            
    def disable_constraint_checking(self):
        with self.cursor() as cursor:
            cursor.execute("SET CONSTRAINTS ALL DEFERRED")
        return True

    def enable_constraint_checking(self):
        pass
            
    def check_constraints(self, table_names=None):
        """
        To check constraints, we set constraints to immediate. Then, when, we're done we must ensure they
        are returned to deferred.
        """
        with self.cursor() as cursor:
            cursor.execute('SET CONSTRAINTS ALL IMMEDIATE')
            cursor.execute('SET CONSTRAINTS ALL DEFERRED')
    
    def is_usable(self):
        try:
            self.connection.ping()
        except Database.Error:
            return False
        else:
            return True
        
    @contextmanager
    def _nodb_cursor(self):
        conn = self.__class__({**self.settings_dict, "NAME": "sysmaster"}, alias=NO_DB_ALIAS)
        try:
            with conn.cursor() as cursor:
                cursor.execute("CLOSE DATABASE")
                yield cursor
        finally:
            conn.close()
            
            