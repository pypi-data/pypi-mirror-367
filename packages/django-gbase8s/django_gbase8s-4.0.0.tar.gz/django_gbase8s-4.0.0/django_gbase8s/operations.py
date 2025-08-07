import datetime
import uuid
import decimal

from django.conf import settings
from django.db.backends.base.operations import BaseDatabaseOperations
from django.utils.regex_helper import _lazy_re_compile
from django.db.models import Exists, Lookup, ExpressionWrapper
from django.db.models.expressions import RawSQL
from django.db.models.sql.where import WhereNode
from django.utils import timezone
from django.utils.encoding import force_str, force_bytes
from django.db import NotSupportedError

from .base import Database
from .utils import GBase8s_datetime, GBase8s_date





class DatabaseOperations(BaseDatabaseOperations):
    
    _extract_format_re = _lazy_re_compile(r"[A-Z_]+")
    compiler_module = "django_gbase8s.compiler"
    cast_char_field_without_max_length = "VARCHAR(2000)"
    cast_data_types = {
        "TextField": cast_char_field_without_max_length,
    }
    
    integer_field_ranges = {
        "SmallIntegerField": (-2147483647, 2147483647),
        "IntegerField": (-2147483647, 2147483647),
        "BigIntegerField": (-9223372036854775807, 9223372036854775807),
        "PositiveBigIntegerField": (0, 9223372036854775807),
        "PositiveSmallIntegerField": (0, 2147483647),
        "PositiveIntegerField": (0, 2147483647),
        "SmallAutoField": (-2147483647, 2147483647),
        "AutoField": (-2147483647, 2147483647),
        "BigAutoField": (-9223372036854775807, 9223372036854775807),
    }
    
    def quote_name(self, name):
        if name.startswith('"') and name.endswith('"'):
            return name  # Quoting once is enough.
        return '"%s"' % name
    
    def date_extract_sql(self, lookup_type, field_name):
        if lookup_type == "week_day":
            # TO_CHAR(field, 'D') returns an integer from 1-7, where 1=Sunday.
            return "TO_CHAR(%s, 'D')" % field_name
        elif lookup_type == "iso_week_day":
            return "TO_CHAR(%s - 1, 'D')" % field_name
        elif lookup_type == "week":
            # IW = ISO week number
            # return "TO_CHAR(%s, 'IW')" % field_name
            raise ValueError(
                "GBase 8s does not support get ISO week numbers yet."
            )
        elif lookup_type == "quarter":
            return "TO_CHAR(%s, 'Q')" % field_name
        elif lookup_type == "iso_year":
            # return "TO_CHAR(%s, 'IYYY')" % field_name
            return "django_isoyear_extract(%s)" % field_name
        else:
            return "EXTRACT(%s FROM %s)" % (lookup_type.upper(), field_name)
    
    def datetime_extract_sql(self, lookup_type, field_name, tzname):
        return self.date_extract_sql(lookup_type, field_name)
    
    def max_name_length(self):
        return 64
    
    def validate_autopk_value(self, value):
        if value == 0 and not self.connection.features.allows_auto_pk_0:
            raise ValueError(
                "The database backend does not accept 0 as a value for AutoField."
            )
        return value
    
    def adapt_datefield_value(self, value):
        if value is None:
            return None
        return GBase8s_date.from_date(value)

    def adapt_timefield_value(self, value):
        if value is None:
            return None

        if hasattr(value, "resolve_expression"):
            return value
        
        if timezone.is_aware(value):
            raise ValueError("GBase 8s backend does not support timezone-aware times.")
        
        return GBase8s_datetime(
            1900, 1, 1, value.hour, value.minute, value.second, value.microsecond
        )
        
    def adapt_datetimefield_value(self, value):
        # handle datetime timezone when bind datetime variable
        if value is None:
            return None
        if timezone.is_aware(value):    # datetime with tiemzone or utcoffset
            if settings.USE_TZ:
                # convert datetiem without timezone to local time
                value = timezone.make_naive(value, self.connection.timezone)
            else:
                raise ValueError(
                    "GBase 8s backend does not support timezone-aware datetimes when "
                    "USE_TZ is False."
                )
        return GBase8s_datetime.from_datetime(value)
    
    def adapt_decimalfield_value(self, value, max_digits=None, decimal_places=None):
        return value
        
    def last_insert_id(self, cursor, table_name, pk_name):
        return cursor.lastrowid    

    def get_db_converters(self, expression):
        converters = super().get_db_converters(expression)
        internal_type = expression.output_field.get_internal_type()
        if internal_type == "DateField":
            converters.append(self.convert_datefield_value)
        elif internal_type == "TextField":
            converters.append(self.convert_textfield_value)
        elif internal_type == "BinaryField":
            converters.append(self.convert_binaryfield_value)
        elif internal_type == "TimeField":
            converters.append(self.convert_timefield_value)
        elif internal_type == "DateTimeField":
            if settings.USE_TZ:
                converters.append(self.convert_datetimefield_value)
        elif internal_type == "UUIDField":
            converters.append(self.convert_uuidfield_value)
        elif internal_type in ("BinaryField","TextField"):
            converters.append(self.convert_lobfield_value)
        elif internal_type == "BooleanField":
            converters.append(self.convert_booleanfield_value)
        elif internal_type == "DecimalField":
            converters.append(self.convert_decimalfield_value)
        elif internal_type == "FloatField":
            converters.append(self.convert_floatfield_value)
        # elif internal_type == "CharField":
        #     converters.append(self.convert_charfield_value)
        if expression.output_field.empty_strings_allowed:
            converters.append(
                self.convert_empty_bytes
                if internal_type == "BinaryField"
                else self.convert_empty_string
            )
        return converters

    
    def convert_empty_string(self, value, expression, connection):
        return "" if value is None else value

    def convert_empty_bytes(self, value, expression, connection):
        return b"" if value is None else value
    
    def convert_charfield_value(self, value, expression, connection):
        # interprets_empty_strings_as_nulls = True
        return None if value == "" else value
    
    def convert_uuidfield_value(self, value, expression, connection):
        if value is not None:
            value = uuid.UUID(value)
        return value
        
    def convert_datefield_value(self, value, expression, connection):
        if isinstance(value, datetime.datetime):
            value = value.date()
        return value
    
    def convert_textfield_value(self, value, expression, connection):
        if isinstance(value, Database.LOB):
            value = value.read()
        return value

    def convert_binaryfield_value(self, value, expression, connection):
        if isinstance(value, Database.LOB):
            value = force_bytes(value.read())
        return value
    
    def convert_timefield_value(self, value, expression, connection):
        if isinstance(value, datetime.datetime):
            value = value.time()
        return value
    
    def convert_datetimefield_value(self, value, expression, connection):
        if value is not None:
            value = timezone.make_aware(value, self.connection.timezone)
        return value
    
    def convert_lobfield_value(self, value, expression, connection):
        if isinstance(value, Database.LOB):
            value = value.read()
        return value
    
    def convert_booleanfield_value(self, value, expression, connection):
        if value in (0, 1):
            value = bool(value)
        return value
    
    def convert_decimalfield_value(self, value, expression, connection):
        if value is not None:
            value = decimal.Decimal(str(value))
        return value
        
    def convert_floatfield_value(self, value, expression, connection):
        if value is not None:
            value = float(value)
        return value
        
    def conditional_expression_supported_in_where_clause(self, expression):
        if isinstance(expression, (Exists, Lookup, WhereNode)):
            return True
        if isinstance(expression, ExpressionWrapper) and expression.conditional:
            return self.conditional_expression_supported_in_where_clause(
                expression.expression
            )
        if isinstance(expression, RawSQL) and expression.conditional:
            return True
        return False
        
    def date_trunc_sql(self, lookup_type, field_name, tzname=None):
        # field_name = self._convert_field_to_tz(field_name, tzname)
        if lookup_type in ("year", "month"):
            return "TRUNC(%s, '%s')" % (field_name, lookup_type.upper())
        elif lookup_type == "quarter":
            return "TRUNC(%s, 'Q')" % field_name
        elif lookup_type == "week":
            return "TRUNC(%s, 'IW')" % field_name
        else:
            return "TRUNC(%s)" % field_name
    
    def datetime_trunc_sql(self, lookup_type, field_name, tzname):
        if lookup_type in ("year", "month"):
            sql = "TRUNC(%s, '%s')" % (field_name, lookup_type.upper())
        elif lookup_type == "quarter":
            sql = "TRUNC(%s, 'Q')" % field_name
        elif lookup_type == "week":
            sql = "TRUNC(%s, 'IW')" % field_name
        elif lookup_type == "day":
            sql = "TRUNC(%s)" % field_name
        elif lookup_type == "hour":
            sql = "TRUNC(%s, 'HH24')" % field_name
        elif lookup_type == "minute":
            sql = "TRUNC(%s, 'MI')" % field_name
        else:
            sql = ("CAST(%s AS TIMESTAMP(0))" % field_name)
        return sql
    
    def time_trunc_sql(self, lookup_type, field_name, tzname=None):
        if lookup_type == "hour":
            sql = "TRUNC(%s, 'HH24')" % field_name
        elif lookup_type == "minute":
            sql = "TRUNC(%s, 'MI')" % field_name
        elif lookup_type == "second":
            # Cast to DATE removes sub-second precision.
            sql =  ("CAST(%s AS TIMESTAMP(0))" % field_name)
        return sql
    
    def datetime_cast_date_sql(self, field_name, tzname):
        return "TRUNC(%s)" % field_name
    
    def datetime_cast_time_sql(self, field_name, tzname):
        # Since `TimeField` values are stored as TIMESTAMP change to the
        # default date and convert the field to the specified timezone.
        # sql, params = self._convert_sql_to_tz(sql, params, tzname)
        convert_datetime_sql = (
            "TO_TIMESTAMP(CONCAT('1900-01-01 ', TO_CHAR(%s, 'HH24:MI:SS.FF')), "
            "'YYYY-MM-DD HH24:MI:SS.FF')"
        % field_name)
        return "CASE WHEN %s IS NOT NULL THEN %s ELSE NULL END" % (
            field_name,
            convert_datetime_sql,
        )

    def pk_default_value(self):
        return "0"

    def last_executed_query(self, cursor, sql, params):   
        """
        Return a string of the query last executed by the given cursor, with
        placeholders replaced with actual values.

        `sql` is the raw query containing placeholders and `params` is the
        sequence of parameters. These are used by default, but this method
        exists for database backends to provide a better implementation
        according to their own quoting schemes.
        """
        sql = cursor.statement
        if not params or not sql:
            return sql
        # Convert params to contain string values.
        def to_string(s):
            return force_str(s, strings_only=False, errors="replace")

        if isinstance(params, (list, tuple)):
            u_params = tuple(to_string(val) for val in params)
            for param in u_params:
                sql = sql.replace('?', to_string(param), 1)
            return sql
        else:
            u_params = {f":{to_string(k)}": to_string(v) for k, v in params.items()}
            for key in sorted(u_params, key=len, reverse=True):
                sql = sql.replace(key, u_params[key])
            return sql
    
    def _get_all_fk_names(self, tables):
        
        placeholders = ", ".join(['%s' for _ in tables])
        sql = f"""
            select t1.constrname, t2.tabname 
            from sysconstraints t1, systables t2
            where t1.tabid = t2.tabid
            and t1.constrid in (
                select constrid from sysreferences 
                where ptabid in (
                    select tabid from systables 
                    where tabname in ({placeholders})
                )
            )
        """
        with self.connection.cursor() as cursor:
            cursor.execute(sql, tables)
            constrnames = []
            cascade_tables = []
            for row in cursor.fetchall():
                constrnames.append(row[0])
                cascade_tables.append(row[1])
        return constrnames, set(cascade_tables)

            
    def sql_flush(self, style, tables, *, reset_sequences=False, allow_cascade=False):
        if not tables:
            return []
        constrnames, cascade_tables = self._get_all_fk_names(tables)
        if cascade_tables:
            tables.extend(list(cascade_tables))
        sql = [
            "%s %s %s %s"
            % (
                style.SQL_KEYWORD("SET"),
                style.SQL_KEYWORD("CONSTRAINTS"),
                style.SQL_FIELD(constrname),
                style.SQL_KEYWORD("DISABLED"),                
            )
            for constrname in constrnames
        ]
        sql.extend([
            "%s %s %s"
            % (
                style.SQL_KEYWORD("TRUNCATE"),
                style.SQL_KEYWORD("TABLE"),
                style.SQL_FIELD(self.quote_name(table)),                
            )
            for table in tables
        ])
        sql.extend([
            "%s %s %s %s"
            % (
                style.SQL_KEYWORD("SET"),
                style.SQL_KEYWORD("CONSTRAINTS"),
                style.SQL_FIELD(constrname),
                style.SQL_KEYWORD("ENABLED"),                
            )
            for constrname in constrnames
        ])
        if reset_sequences:
            with self.connection.cursor() as cursor:
                for table in tables:
                    seqs = self.connection.introspection.get_sequences(cursor, table)
                    if seqs:
                        sql.append(
                            "ALTER TABLE %s MODIFY %s SERIAL (1) PRIMARY KEY" 
                            % (
                                style.SQL_FIELD(table),
                                style.SQL_FIELD(seqs[0]['column'])
                            )
                        )
        return sql
    
    def limit_offset_sql(self, low_mark, high_mark):
        fetch, offset = self._get_limit_offset_params(low_mark, high_mark)
        return " ".join(
            sql
            for sql in (
                ("SKIP %d " % offset) if offset else None,
                ("FIRST %d " % fetch) if fetch else None,
            )
            if sql
        )
        
    def process_clob(self, value):
        if value is None:
            return ""
        return value.read()
        
        
    def lookup_cast(self, lookup_type, internal_type=None):
        field = '%s'
        # upper function and like expression need string
        if lookup_type in ("iexact", "contains", "startswith", "endswith", "icontains", "istartswith", "iendswith"):
            if internal_type in ("SmallAutoField", "AutoField", "BigAutoField", 
                                 "DateField", "DateTimeField", "TimeField",
                                 "IntegerField", "BigIntegerField", "OneToOneField",
                                 "PositiveIntegerField", "PositiveSmallIntegerField", "PositiveBigIntegerField",
                                 "TextField"
                                 ):
                field = f"%s||''"
        # if ignore case, covert to upper to compare
        if lookup_type in ("iexact", "icontains", "istartswith", "iendswith"):
                return f"UPPER({field})"
        return field
    
    def no_limit_value(self):
        return None
    
    def regex_lookup(self, lookup_type):
        if lookup_type == "regex":
            match_option = "'c'"
        else:
            match_option = "'i'"
        return "REGEXP_LIKE(%%s, %%s, %s)" % match_option
    
    def conditional_expression_supported_in_where_clause(self, expression):
        if isinstance(expression, (Exists, Lookup, WhereNode)):
            return True
        if isinstance(expression, ExpressionWrapper) and expression.conditional:
            return self.conditional_expression_supported_in_where_clause(
                expression.expression
            )
        if isinstance(expression, RawSQL) and expression.conditional:
            return True
        return False
    
    def combine_expression(self, connector, sub_expressions):
        lhs, rhs = sub_expressions
        if connector == "%%":
            return "MOD(%s)" % ",".join(sub_expressions)
        elif connector == "&":
            return "BITAND(%s)" % ",".join(sub_expressions)
        elif connector == "|":
            return "BITAND(-%(lhs)s-1,%(rhs)s)+%(lhs)s" % {"lhs": lhs, "rhs": rhs}
        elif connector == "<<":
            return "(%(lhs)s * POWER(2, %(rhs)s))" % {"lhs": lhs, "rhs": rhs}
        elif connector == ">>":
            return "FLOOR(%(lhs)s / POWER(2, %(rhs)s))" % {"lhs": lhs, "rhs": rhs}
        elif connector == "^":
            return "POWER(%s)" % ",".join(sub_expressions)
        elif connector == "#":
            raise NotSupportedError("Bitwise XOR is not supported in GBase 8s.")
        return super().combine_expression(connector, sub_expressions)
    
    def prep_for_iexact_query(self, x):
        return x

    def bulk_insert_sql(self, fields, placeholder_rows):
        placeholder_rows_sql = (", ".join(row) for row in placeholder_rows)
        values_sql = ", ".join([f"({sql})" for sql in placeholder_rows_sql])
        return f"VALUES {values_sql}"
        