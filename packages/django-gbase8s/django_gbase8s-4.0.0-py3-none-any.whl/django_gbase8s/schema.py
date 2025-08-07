import copy
import datetime
import re

from django.db import DatabaseError
from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from django.db.backends.base.schema import _related_non_m2m_objects
from django.utils.duration import _get_duration_components
from django.db.backends.utils import split_identifier
from django.db.models import NOT_PROVIDED, Deferrable, Index
from django.db.backends.ddl_references import (
    Columns,
    Expressions,
    ForeignKeyName,
    IndexName,
    Statement,
    Table,
)

class DatabaseSchemaEditor(BaseDatabaseSchemaEditor):
    sql_create_column = "ALTER TABLE %(table)s ADD %(column)s %(definition)s"
    sql_alter_column_type = "MODIFY %(column)s %(type)s"
    sql_alter_column_null = "MODIFY %(column)s NULL"
    sql_alter_column_not_null = "MODIFY %(column)s NOT NULL"
    sql_alter_column_default = "MODIFY %(column)s DEFAULT %(default)s"
    sql_alter_column_no_default = "MODIFY %(column)s DEFAULT NULL"
    sql_alter_column_no_default_null = sql_alter_column_no_default
    sql_delete_column = "ALTER TABLE %(table)s DROP COLUMN %(column)s"
    sql_create_column_inline_fk = (
        "CONSTRAINT %(name)s REFERENCES %(to_table)s(%(to_column)s)%(deferrable)s"
    )
    sql_delete_table = "DROP TABLE %(table)s CASCADE CONSTRAINTS"
    sql_create_index = "CREATE INDEX IF NOT EXISTS %(name)s ON %(table)s (%(columns)s) %(extra)s"
    sql_rename_index = "RENAME INDEX %(old_name)s TO %(new_name)s"

    
    @staticmethod
    def _duration_string(duration):
        """Version of str(timedelta) which is not English specific."""
        days, hours, minutes, seconds, microseconds = _get_duration_components(duration)

        string = "{} {:02d}:{:02d}:{:02d}".format(days, hours, minutes, seconds)
        if microseconds:
            string += ".{:06d}".format(microseconds)

        return string
    
    def quote_value(self, value):
        if isinstance(value, (datetime.date, datetime.time, datetime.datetime)):
            return "'%s'" % value
        elif isinstance(value, datetime.timedelta):
            return "'%s'" % self._duration_string(value)
        elif isinstance(value, str):
            return "'%s'" % value.replace("'", "''")
        elif isinstance(value, (bytes, bytearray, memoryview)):
            return "'%s'" % value.hex()
        elif isinstance(value, bool):
            return "1" if value else "0"
        else:
            return str(value)

    def prepare_default(self, value):
        if value == "":
            return 'NULL'
        return self.quote_value(value)
            
        
    def _create_index_name(self, table_name, column_names, suffix=""):
        column_names = [split_identifier(c)[1] for c in column_names]
        return super()._create_index_name(table_name, column_names, suffix)
    
    def _alter_field(
            self,
            model,
            old_field,
            new_field,
            old_type,
            new_type,
            old_db_params,
            new_db_params,
            strict=False,
        ):
            """Perform a "physical" (non-ManyToMany) field update."""
            # Drop any FK constraints, we'll remake them later            
            fks_dropped = set()
            if (
                self.connection.features.supports_foreign_keys
                and old_field.remote_field
                and old_field.db_constraint
            ):
                fk_names = self._constraint_names(
                    model, [old_field.column], foreign_key=True
                )
                if strict and len(fk_names) != 1:
                    raise ValueError(
                        "Found wrong number (%s) of foreign key constraints for %s.%s"
                        % (
                            len(fk_names),
                            model._meta.db_table,
                            old_field.column,
                        )
                    )
                for fk_name in fk_names:
                    fks_dropped.add((old_field.column,))
                    self.execute(self._delete_fk_sql(model, fk_name))
            
            # If primary_key changed to False, delete the primary key constraint.
            if old_field.primary_key and not new_field.primary_key:
                self._delete_primary_key(model, strict)
                
            # Has unique been removed?
            if old_field.unique and (
                not new_field.unique or self._field_became_primary_key(old_field, new_field)
            ):
                # Find the unique constraint for this field
                meta_constraint_names = {
                    constraint.name for constraint in model._meta.constraints
                }
                constraint_names = self._constraint_names(
                    model,
                    [old_field.column],
                    unique=True,
                    primary_key=False,
                    exclude=meta_constraint_names,
                )
                if strict and len(constraint_names) != 1:
                    raise ValueError(
                        "Found wrong number (%s) of unique constraints for %s.%s"
                        % (
                            len(constraint_names),
                            model._meta.db_table,
                            old_field.column,
                        )
                    )
                for constraint_name in constraint_names:
                    self.execute(self._delete_unique_sql(model, constraint_name))
            # Drop incoming FK constraints if the field is a primary key or unique,
            # which might be a to_field target, and things are going to change.
            # old_collation = old_db_params.get("collation")
            # new_collation = new_db_params.get("collation")
            drop_foreign_keys = (
                self.connection.features.supports_foreign_keys
                and (
                    (old_field.primary_key and new_field.primary_key)
                    or (old_field.unique and new_field.unique)
                )
                and old_type != new_type
            )
            if drop_foreign_keys:
                # '_meta.related_field' also contains M2M reverse fields, these
                # will be filtered out
                for _old_rel, new_rel in _related_non_m2m_objects(old_field, new_field):
                    rel_fk_names = self._constraint_names(
                        new_rel.related_model, [new_rel.field.column], foreign_key=True
                    )
                    for fk_name in rel_fk_names:
                        self.execute(self._delete_fk_sql(new_rel.related_model, fk_name))
            if (
                old_field.db_index
                and not old_field.unique
                and (not new_field.db_index or new_field.unique)
            ):
                # Find the index for this field
                meta_index_names = {index.name for index in model._meta.indexes}
                # Retrieve only BTREE indexes since this is what's created with
                # db_index=True.
                index_names = self._constraint_names(
                    model,
                    [old_field.column],
                    index=True,
                    type_=Index.suffix,
                    exclude=meta_index_names,
                )
                for index_name in index_names:
                    # The only way to check if an index was created with
                    # db_index=True or with Index(['field'], name='foo')
                    # is to look at its name (refs #28053).
                    self.execute(self._delete_index_sql(model, index_name))
            # Change check constraints?
            # old_db_check = self._field_db_check(old_field, old_db_params)
            # new_db_check = self._field_db_check(new_field, new_db_params)
            if old_db_params["check"] != new_db_params["check"] and old_db_params["check"]:
                meta_constraint_names = {
                    constraint.name for constraint in model._meta.constraints
                }
                constraint_names = self._constraint_names(
                    model,
                    [old_field.column],
                    check=True,
                    exclude=meta_constraint_names,
                )
                if strict and len(constraint_names) != 1:
                    raise ValueError(
                        "Found wrong number (%s) of check constraints for %s.%s"
                        % (
                            len(constraint_names),
                            model._meta.db_table,
                            old_field.column,
                        )
                    )
                for constraint_name in constraint_names:
                    self.execute(self._delete_check_sql(model, constraint_name))            
            # Have they renamed the column?
            if old_field.column != new_field.column:
                self.execute(
                    self._rename_field_sql(
                        model._meta.db_table, old_field, new_field, new_type
                    )
                )
                # Rename all references to the renamed column.
                for sql in self.deferred_sql:
                    if isinstance(sql, Statement):
                        sql.rename_column_references(
                            model._meta.db_table, old_field.column, new_field.column
                        )
            # Next, start accumulating actions to do
            actions = []
            null_actions = []
            post_actions = []
            # Collation change?
            old_collation = getattr(old_field, "db_collation", None)
            new_collation = getattr(new_field, "db_collation", None)
            if old_collation != new_collation:
                # Collation change handles also a type change.
                fragment = self._alter_column_collation_sql(
                    model, new_field, new_type, new_collation
                )
                actions.append(fragment)
            # Type change?
            elif old_type != new_type:
                fragment, other_actions = self._alter_column_type_sql(
                    model, old_field, new_field, new_type
                )
                actions.append(fragment)
                post_actions.extend(other_actions) 
            needs_database_default = False
            if old_field.null and not new_field.null:
                old_default = self.effective_default(old_field)
                new_default = self.effective_default(new_field)
                if (
                    not self.skip_default_on_alter(new_field)
                    and old_default != new_default
                    and new_default is not None
                ):
                    needs_database_default = True
                    actions.append(
                        self._alter_column_default_sql(model, old_field, new_field)
                    )
            # Nullability change?
            if old_field.null != new_field.null:          
                fragment = self._alter_column_null_sql(model, old_field, new_field)
                if fragment:
                    null_actions.append(fragment)
            elif len(actions) > 0 and not new_field.null and not old_field.empty_strings_allowed:
                new_db_params = new_field.db_parameters(connection=self.connection)
                fragment = self.sql_alter_column_not_null % {
                    "column": self.quote_name(new_field.column),
                    "type": new_db_params["type"],
                }, []
                null_actions.append(fragment)
                
            # Only if we have a default and there is a change from NULL to NOT NULL
            four_way_default_alteration = new_field.has_default() and (
                old_field.null and not new_field.null
            )
            if actions or null_actions:
                if not four_way_default_alteration:
                    # If we don't have to do a 4-way default alteration we can
                    # directly run a (NOT) NULL alteration
                    all_actions = actions + null_actions
                else:
                    all_actions = actions
                # Apply those actions
                for sql, params in all_actions:
                    self.execute(
                        self.sql_alter_column
                        % {
                            "table": self.quote_name(model._meta.db_table),
                            "changes": sql,
                        },
                        params,
                    )
                if four_way_default_alteration:
                    # if new_field.db_default is NOT_PROVIDED:
                    default_sql = "%s"
                    params = [new_default]
                    # else:
                    #     default_sql, params = self.db_default_sql(new_field)
                    # Update existing rows with default value
                    self.execute(
                        self.sql_update_with_default
                        % {
                            "table": self.quote_name(model._meta.db_table),
                            "column": self.quote_name(new_field.column),
                            "default": default_sql,
                        },
                        params,
                    )
                    # Drop the default if we need to
                    # (Django usually does not use in-database defaults)
                    if needs_database_default:
                        changes_sql, params = self._alter_column_default_sql(
                            model, old_field, new_field, drop=True
                        )
                        sql = self.sql_alter_column % {
                            "table": self.quote_name(model._meta.db_table),
                            "changes": changes_sql,
                        }
                        self.execute(sql, params)
                    # Since we didn't run a NOT NULL change before we need to do it
                    # now
                    for sql, params in null_actions:
                        self.execute(
                            self.sql_alter_column
                            % {
                                "table": self.quote_name(model._meta.db_table),
                                "changes": sql,
                            },
                            params,
                        )
            if post_actions:
                for sql, params in post_actions:
                    self.execute(sql, params)
            # Added a unique?
            if (self._unique_should_be_added(old_field, new_field)
                or (len(actions) > 0 and not new_field.primary_key and new_field.unique)
            ):
                self.execute(self._create_unique_sql(model, [new_field]))
                
            # Added index?
            if (
                (not old_field.db_index or old_field.unique)
                and new_field.db_index
                and not new_field.unique
            ):
                self.execute(self._create_index_sql(model, fields=[new_field]))
            # Type alteration on primary key? Then we need to alter the column
            # referring to us.
            rels_to_update = []
            if drop_foreign_keys:
                rels_to_update.extend(_related_non_m2m_objects(old_field, new_field))            
            # Changed to become primary key?
            if (self._field_became_primary_key(old_field, new_field)
                or (len(actions) > 0 and new_field.primary_key)
            ):
                # Make the new one
                self.execute(self._create_primary_key_sql(model, new_field))
                if self._field_became_primary_key(old_field, new_field):
                    # Update all referencing columns
                    rels_to_update.extend(_related_non_m2m_objects(old_field, new_field))
            # Handle our type alters on the other end of rels from the PK stuff above
            for old_rel, new_rel in rels_to_update:
                rel_db_params = new_rel.field.db_parameters(connection=self.connection)
                rel_type = rel_db_params["type"]
                rel_collation = rel_db_params.get("collation")
                old_rel_db_params = old_rel.field.db_parameters(connection=self.connection)
                old_rel_collation = old_rel_db_params.get("collation")
                fragment, other_actions = self._alter_column_type_sql(
                    new_rel.related_model,
                    old_rel.field,
                    new_rel.field,
                    rel_type,
                    # old_rel_collation,
                    # rel_collation,
                )
                self.execute(
                    self.sql_alter_column
                    % {
                        "table": self.quote_name(new_rel.related_model._meta.db_table),
                        "changes": fragment[0],
                    },
                    fragment[1],
                )
                for sql, params in other_actions:   # comment
                    self.execute(sql, params)
                # need primary key?
                if new_rel.field.primary_key:
                    self.execute(self._create_primary_key_sql(new_rel.related_model, new_rel.field))
                # need add not null?
                elif not new_rel.field.null:
                    sql, params = self._alter_column_null_sql(new_rel.related_model, old_rel.field, new_rel.field)
                    self.execute(
                        self.sql_alter_column
                        % {
                            "table": self.quote_name(new_rel.related_model._meta.db_table),
                            "changes": sql
                        },
                        params,
                    )
            # Does it have a foreign key?
            if (
                self.connection.features.supports_foreign_keys
                and new_field.remote_field
                and (
                    fks_dropped or not old_field.remote_field or not old_field.db_constraint
                )
                and new_field.db_constraint
            ):
                self.execute(
                    self._create_fk_sql(model, new_field, "_fk_%(to_table)s_%(to_column)s")
                )
            # Rebuild FKs that pointed to us if we previously had to drop them
            if drop_foreign_keys:
                for _, rel in rels_to_update:
                    if rel.field.db_constraint:
                        self.execute(
                            self._create_fk_sql(rel.related_model, rel.field, "_fk")
                        )
            # Does it have check constraints we need to add?
            if old_db_params["check"] != new_db_params["check"] and new_db_params["check"]:
                constraint_name = self._create_index_name(
                    model._meta.db_table, [new_field.column], suffix="_check"
                )
                self.execute(
                    self._create_check_sql(model, constraint_name, new_db_params["check"])
                )
            if self.connection.features.connection_persists_old_columns:
                self.connection.close()

    def _field_should_be_indexed(self, model, field):
        create_index = super()._field_should_be_indexed(model, field)
        db_type = field.db_type(self.connection)
        if (
            db_type is not None
            and db_type.lower() in self.connection._limited_data_types
        ):
            return False
        return create_index

    def _field_db_check(self, field, field_db_params):
        # Always check constraints with the same mocked column name to avoid
        # recreating constrains when the column is renamed.
        check_constraints = self.connection.data_type_check_constraints
        data = field.db_type_parameters(self.connection)
        data["column"] = "__column_name__"
        try:
            return check_constraints[field.get_internal_type()] % data
        except KeyError:
            return None

    def _unique_should_be_added(self, old_field, new_field):
        return (
            not new_field.primary_key
            and new_field.unique
            and (not old_field.unique or old_field.primary_key)
        )

    def alter_field(self, model, old_field, new_field, strict=False):
        try:
            super().alter_field(model, old_field, new_field, strict)
        except DatabaseError as e:
            description = str(e)
            if "-9633" in description:
                self._alter_field_type_workaround(model, old_field, new_field)
            else:
                raise

    def _alter_field_type_workaround(self, model, old_field, new_field):
        # Make a new field that's like the new one but with a temporary
        # column name.
        new_temp_field = copy.deepcopy(new_field)
        new_temp_field.null = new_field.get_internal_type() not in (
            "AutoField",
            "BigAutoField",
            "SmallAutoField",
        )
        new_temp_field.column = self._generate_temp_name(new_field.column)
        # Add it
        self.add_field(model, new_temp_field)
        new_value = self.quote_name(old_field.column)
        old_type = old_field.db_type(self.connection)
        if re.match("^N?CLOB", old_type):
            new_value = "TO_CHAR(%s)" % new_value
            old_type = "VARCHAR2"
        if re.match("^N?VARCHAR2", old_type):
            new_internal_type = new_field.get_internal_type()
            if new_internal_type == "DateField":
                new_value = "TO_DATE(%s, 'YYYY-MM-DD')" % new_value
            elif new_internal_type == "DateTimeField":
                new_value = "TO_TIMESTAMP(%s, 'YYYY-MM-DD HH24:MI:SS.FF')" % new_value
            elif new_internal_type == "TimeField":
                new_value = "CONCAT('1900-01-01 ', %s)" % new_value
                new_value = "TO_TIMESTAMP(%s, 'YYYY-MM-DD HH24:MI:SS.FF')" % new_value
        self.execute(
            "UPDATE %s set %s=%s"
            % (
                self.quote_name(model._meta.db_table),
                self.quote_name(new_temp_field.column),
                new_value,
            )
        )
        self.remove_field(model, old_field)
        super().alter_field(model, new_temp_field, new_field)
        new_type = new_field.db_type(self.connection)
        if (
            (old_field.primary_key and new_field.primary_key)
            or (old_field.unique and new_field.unique)
        ) and old_type != new_type:
            for _, rel in _related_non_m2m_objects(new_temp_field, new_field):
                if rel.field.db_constraint:
                    self.execute(
                        self._create_fk_sql(rel.related_model, rel.field, "_fk")
                    )

    def _generate_temp_name(self, for_name):
        """Generate temporary names for workarounds that need temp columns."""
        suffix = hex(hash(for_name)).upper()[1:]
        return for_name + "_" + suffix