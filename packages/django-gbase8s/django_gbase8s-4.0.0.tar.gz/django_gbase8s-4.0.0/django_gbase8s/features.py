from django.db import InterfaceError
from django.db.backends.base.features import BaseDatabaseFeatures
from django.utils.functional import cached_property

class DatabaseFeatures(BaseDatabaseFeatures):
    minimum_database_version = (8, 8)
    allows_group_by_lob = False
    allows_group_by_select_index = True  # group by 1
    delete_can_self_reference_subquery = False
    interprets_empty_strings_as_nulls = True
    supports_nullable_unique_constraints = False
    supports_partially_nullable_unique_constraints = False
    # supports_deferrable_unique_constraints = True
    has_select_for_update = True
    has_select_for_update_nowait = True
    has_select_for_update_skip_locked = True
    has_select_for_update_of = True
    select_for_update_of_column = True
    supports_forward_references = False
    supports_subqueries_in_group_by = False
    ignores_unnecessary_order_by_in_subqueries = False
    supports_partial_indexes = False


    supports_regex_backreferencing = False
    can_rollback_ddl = False
    uses_savepoints = True
    can_release_savepoints = True    
    supports_timezones = False    
    supports_sequence_reset = False    
    supports_tablespaces = False      
    closed_cursor_error_class = InterfaceError
    
    has_native_duration_field = True
    supports_temporal_subtraction = True
    nulls_order_largest = False
    max_query_params = 2**16 - 1
    # can_defer_constraint_checks = True
    supports_default_keyword_in_insert = False
    allows_auto_pk_0 = False
    has_json_object_function = False
    supports_timezones = False

    @cached_property
    def introspected_field_types(self):
        return {
            **super().introspected_field_types,
            "GenericIPAddressField": "CharField",
            "PositiveBigIntegerField": "BigIntegerField",
            "PositiveIntegerField": "IntegerField",
            "PositiveSmallIntegerField": "IntegerField",
            "SmallIntegerField": "IntegerField",
            "SmallAutoField": "AutoField",
            "TimeField": "DateTimeField",
        }
    
    can_introspect_materialized_views = True
    atomic_transactions = False
    can_rename_index = True
    requires_literal_defaults = True  
    bare_select_suffix = " FROM DUAL"
    supports_select_for_update_with_limit = False
    ignores_table_name_case = False
    # requires_compound_order_by_subquery = True
    supports_index_on_text_field = False
    supports_over_clause = True
    supports_frame_range_fixed_distance = True
    create_test_procedure_without_params_sql = """
        CREATE PROCEDURE "test_procedure" AS
            V_I INTEGER;
        BEGIN
            V_I := 1;
        END;
    """
    create_test_procedure_with_int_param_sql = """
        CREATE PROCEDURE "test_procedure" (P_I INTEGER) AS
            V_I INTEGER;
        BEGIN
            V_I := P_I;
        END;
    """
    create_test_table_with_composite_primary_key = """
        CREATE TABLE test_table_composite_pk (
            column_1 NUMBER(11) NOT NULL,
            column_2 NUMBER(11) NOT NULL,
            PRIMARY KEY (column_1, column_2)
        )
    """
    # insert_test_table_with_defaults = 'INSERT INTO {} ("null") VALUES (1)'
    supports_callproc_kwargs = True
    supports_ignore_conflicts = False
    supports_partial_indexes = False
    allows_multiple_constraints_on_same_fields = False
    supports_json_field = False
    supports_boolean_expr_in_select_clause = False
    supports_comparing_boolean_expr = False
    supports_primitives_in_json_field = False
    supports_json_field_contains = False
    supports_collation_on_charfield = False
    supports_collation_on_textfield = False
    supports_non_deterministic_collations = False
    supports_comments = True
    supports_comments_inline = False
    # test_now_utc_template = "CURRENT_TIMESTAMP AT TIME ZONE 'UTC'"
    rounds_to_even = True
    
    supports_transactions = True
    indexes_foreign_keys = True
    supports_expression_indexes = False
    supports_boolean_expr_in_select_clause = False  # user 0 and 1
    
    @cached_property
    def django_test_skips(self):
        skips = {
            "GBase 8s doesn't support bool expression in select clause.": {
                "lookup.tests.LookupQueryingTests.test_aggregate_combined_lookup",
            },
        }
        return skips
