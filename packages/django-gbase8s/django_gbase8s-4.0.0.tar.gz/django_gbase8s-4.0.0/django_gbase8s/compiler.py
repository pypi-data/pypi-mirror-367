import math
from django.db.models.sql import compiler
from django.utils.hashable import make_hashable
from django.db.models.functions import (
    Pi as BasePi,
    Random as BaseRandom,
    Length as BaseLength,
    Repeat as BaseRepeat,
    RPad as BaseRPad,
    Chr as BaseChr,
    Reverse as BaseReverse,
    Substr as BaseSubstr,
    Ceil as BaseCeil,
    Cot as BaseCot,
    Degrees as BaseDegrees,
    Radians as BaseRadians,
    Now as BaseNow,
    Cast as BaseCast,
    JSONObject as BaseJSONObject,
    NullIf as BaseNullIf,

)
from django.db.models.aggregates import(
    Max as BaseMax,
    Min as BaseMin,
    Aggregate as BaseAggregate,
)
from django.db.models.lookups import(
    Lookup as BaseLookup,
)
from django.db.models.expressions import Value, Case, When, Func, Ref
from django.core.exceptions import EmptyResultSet
from django.db import NotSupportedError


class NullIf(BaseNullIf):
    def as_gbase8s(self, compiler, connection, **extra_context):
        expression1 = self.get_source_expressions()[0]
        if isinstance(expression1, Value) and expression1.value is None:
            raise ValueError("GBase 8s does not allow Value(None) for expression1.")
        return super().as_sql(compiler, connection, **extra_context)


class JSONObject(BaseJSONObject):
    
    def as_gbase8s(self, compiler, connection, **extra_context):
        return self.as_native(compiler, connection, returning="CLOB", **extra_context)


class Cast(BaseCast):
    
    def as_gbase8s(self, compiler, connection, **extra_context):
        if self.output_field.get_internal_type() == "JSONField":
            template = "JSON_QUERY(%(expressions)s, '$')"
            return super().as_sql(
                compiler, connection, template=template, **extra_context
            )
        return self.as_sql(compiler, connection, **extra_context)


class Now(BaseNow):
    
    def as_gbase8s(self, compiler, connection, **extra_context):
        return self.as_sql(
            compiler, connection, template="LOCALTIMESTAMP", **extra_context
        )


class Radians(BaseRadians):
    
    def as_gbase8s(self, compiler, connection, **extra_context):
        return super().as_sql(
            compiler,
            connection,
            template="((%%(expressions)s) * %s / 180)" % math.pi,
            **extra_context,
        )


class Degrees(BaseDegrees):
    
    def as_gbase8s(self, compiler, connection, **extra_context):
        return super().as_sql(
            compiler,
            connection,
            template="((%%(expressions)s) * 180 / %s)" % math.pi,
            **extra_context,
        )


class Cot(BaseCot):
    
    def as_gbase8s(self, compiler, connection, **extra_context):
        return super().as_sql(
            compiler, connection, template="(1 / TAN(%(expressions)s))", **extra_context
        )


class Ceil(BaseCeil):
    
    def as_gbase8s(self, compiler, connection, **extra_context):
        return super().as_sql(compiler, connection, function="CEIL", **extra_context)


class Chr(BaseChr):
    
    def as_gbase8s(self, compiler, connection, **extra_context):
        return super().as_sql(
            compiler,
            connection,
            template="%(function)s(%(expressions)s USING NCHAR_CS)",
            **extra_context,
        )


class Reverse(BaseReverse):
    
    def as_gbase8s(self, compiler, connection, **extra_context):
        suffix = connection.features.bare_select_suffix
        sql, params = super().as_sql(
            compiler,
            connection,
            template=(
                "(SELECT LISTAGG(s) WITHIN GROUP (ORDER BY n DESC) FROM "
                f"(SELECT LEVEL n, SUBSTR(%(expressions)s, LEVEL, 1) s{suffix} "
                "CONNECT BY LEVEL <= LENGTH(%(expressions)s)) "
                "GROUP BY %(expressions)s)"
            ),
            **extra_context,
        )
        return sql, params * 3
    
    
class Substr(BaseSubstr):
    
    def as_gbase8s(self, compiler, connection, **extra_context):
        return super().as_sql(compiler, connection, function="SUBSTR", **extra_context)
 

class Lookup(BaseLookup):    
        
    def as_gbase8s(self, compiler, connection):
        wrapped = False
        exprs = []
        for expr in (self.lhs, self.rhs):
            if connection.ops.conditional_expression_supported_in_where_clause(expr):
                expr = Case(When(expr, then=True), default=False)
                wrapped = True
            exprs.append(expr)
        lookup = type(self)(*exprs) if wrapped else self
        return lookup.as_sql(compiler, connection)


class Pi(BasePi):    
   
    def as_gbase8s(self, compiler, connection, **extra_context):
        return super(BasePi, self).as_sql(
            compiler, connection, template=str(math.pi), **extra_context
        )
      
        
class Random(BaseRandom):
    
    def as_gbase8s(self, compiler, connection, **extra_context):
        return super(BaseRandom, self).as_sql(
            compiler, connection, function="DBMS_RANDOM.VALUE", **extra_context
        )
     
        
class Max(BaseMax):    
    
    def as_gbase8s(self, compiler, connection, **extra_context):
        sql, params =  self.as_sql(compiler, connection, **extra_context)
        if sql == "MAX(NULL)":
            sql = "NULL"
        return sql, params
  
     
class Min(BaseMin):
    
    def as_gbase8s(self, compiler, connection, **extra_context):
        sql, params =  self.as_sql(compiler, connection, **extra_context)
        if sql == "MIN(NULL)":
            sql = "NULL"
        return sql, params   
     
        
class SQLCompiler(compiler.SQLCompiler):
    
    # BaseRepeat.as_gbase8s = Repeat.as_gbase8s
    BasePi.as_gbase8s = Pi.as_gbase8s
    BaseRandom.as_gbase8s = Random.as_gbase8s
    BaseMin.as_gbase8s = Min.as_gbase8s
    BaseMax.as_gbase8s = Max.as_gbase8s
    BaseLookup.as_gbase8s = Lookup.as_gbase8s
    
    def get_qualify_sql(self):
        where_parts = []
        if self.where:
            where_parts.append(self.where)
        if self.having:
            where_parts.append(self.having)
        inner_query = self.query.clone()
        inner_query.subquery = True
        inner_query.where = inner_query.where.__class__(where_parts)
        # Augment the inner query with any window function references that
        # might have been masked via values() and alias(). If any masked
        # aliases are added they'll be masked again to avoid fetching
        # the data in the `if qual_aliases` branch below.
        select = {
            expr: alias for expr, _, alias in self.get_select(with_col_aliases=True)[0]
        }
        select_aliases = set(select.values())
        qual_aliases = set()
        replacements = {}

        def collect_replacements(expressions):
            while expressions:
                expr = expressions.pop()
                if expr in replacements:
                    continue
                elif select_alias := select.get(expr):
                    replacements[expr] = select_alias
                elif isinstance(expr, BaseLookup):
                    expressions.extend(expr.get_source_expressions())
                elif isinstance(expr, Ref):
                    if expr.refs not in select_aliases:
                        expressions.extend(expr.get_source_expressions())
                else:
                    num_qual_alias = len(qual_aliases)
                    select_alias = f"qual{num_qual_alias}"
                    qual_aliases.add(select_alias)
                    inner_query.add_annotation(expr, select_alias)
                    replacements[expr] = select_alias

        collect_replacements(list(self.qualify.leaves()))
        self.qualify = self.qualify.replace_expressions(
            {expr: Ref(alias, expr) for expr, alias in replacements.items()}
        )
        order_by = []
        for order_by_expr, *_ in self.get_order_by():
            collect_replacements(order_by_expr.get_source_expressions())
            order_by.append(
                order_by_expr.replace_expressions(
                    {expr: Ref(alias, expr) for expr, alias in replacements.items()}
                )
            )
        inner_query_compiler = inner_query.get_compiler(
            self.using, connection=self.connection, elide_empty=self.elide_empty
        )
        inner_sql, inner_params = inner_query_compiler.as_sql(
            # The limits must be applied to the outer query to avoid pruning
            # results too eagerly.
            with_limits=False,
            # Force unique aliasing of selected columns to avoid collisions
            # and make rhs predicates referencing easier.
            with_col_aliases=True,
        )
        qualify_sql, qualify_params = self.compile(self.qualify)
        result = [
            "SELECT "," * FROM (",
            inner_sql,
            ")",
            self.connection.ops.quote_name("qualify"),
            "WHERE",
            qualify_sql,
        ]
        if qual_aliases:
            # If some select aliases were unmasked for filtering purposes they
            # must be masked back.
            cols = [self.connection.ops.quote_name(alias) for alias in select.values()]
            result = [
                "SELECT",
                ", ".join(cols),
                "FROM (",
                *result,
                ")",
                self.connection.ops.quote_name("qualify_mask"),
            ]
        params = list(inner_params) + qualify_params
        # As the SQL spec is unclear on whether or not derived tables
        # ordering must propagate it has to be explicitly repeated on the
        # outer-most query to ensure it's preserved.
        if order_by:
            ordering_sqls = []
            for ordering in order_by:
                ordering_sql, ordering_params = self.compile(ordering)
                ordering_sqls.append(ordering_sql)
                params.extend(ordering_params)
            result.extend(["ORDER BY", ", ".join(ordering_sqls)])
        return result, params

    
    def as_sql(self, with_limits=True, with_col_aliases=False):
        """
        Create the SQL for this query. Return the SQL string and list of
        parameters.

        If 'with_limits' is False, any limit/offset information is not included
        in the query.
        """
        refcounts_before = self.query.alias_refcount.copy()
        try:
            # combinator = self.query.combinator
            extra_select, order_by, group_by = self.pre_sql_setup()
            if with_col_aliases:
                new_select = []
                col_index = 1
                for _s in self.select:
                    if _s[2] is None:
                        _s = list(_s)
                        _s[2] = f"col{col_index}"                        
                        col_index += 1
                        _s = tuple(_s)
                    new_select.append(_s)
                self.select = new_select

            for_update_part = None
            # Is a LIMIT/OFFSET clause needed?
            with_limit_offset = with_limits and (
                self.query.high_mark is not None or self.query.low_mark
            )
            combinator = self.query.combinator
            features = self.connection.features
            if combinator:
                if not getattr(features, "supports_select_{}".format(combinator)):
                    raise NotSupportedError(
                        "{} is not supported on this database backend.".format(
                            combinator
                        )
                    )
                result, params = self.get_combinator_sql(
                    combinator, self.query.combinator_all
                )
            # elif self.qualify:
            #     result, params = self.get_qualify_sql()
            #     order_by = None
            else:
                distinct_fields, distinct_params = self.get_distinct()
                # This must come after 'select', 'ordering', and 'distinct'
                # (see docstring of get_from_clause() for details).
                from_, f_params = self.get_from_clause()
                try:
                    where, w_params = (
                        self.compile(self.where) if self.where is not None else ("", [])
                    )
                except EmptyResultSet:
                    if self.elide_empty:
                        raise
                    # Use a predicate that's always False.
                    where, w_params = "0 = 1", []
                # except FullResultSet:
                    # where, w_params = "", []
                # try:
                having, h_params = (
                        self.compile(self.having)
                        if self.having is not None
                        else ("", [])
                    )
                # except FullResultSet:
                #     having, h_params = "", []
                result = ["SELECT"]
                params = []


                if self.query.distinct:
                    distinct_result, distinct_params = self.connection.ops.distinct_sql(
                        distinct_fields,
                        distinct_params,
                    )
                    result += distinct_result
                    params += distinct_params

                out_cols = []
                for _, (s_sql, s_params), alias in self.select + extra_select:
                    if alias:
                        s_sql = "%s AS %s" % (
                            s_sql,
                            self.connection.ops.quote_name(alias),
                        )

                    params.extend(s_params)
                    out_cols.append(s_sql)

                result += [", ".join(out_cols)]
                if from_:
                    result += ["FROM", *from_]
                # elif self.connection.features.bare_select_suffix:
                #     result += [self.connection.features.bare_select_suffix]
                params.extend(f_params)

                if self.query.select_for_update and features.has_select_for_update:
                    if self.connection.get_autocommit():
                        raise TransactionManagementError(
                            "select_for_update cannot be used outside of a transaction."
                        )

                    if (
                        with_limit_offset
                        and not features.supports_select_for_update_with_limit
                    ):
                        raise NotSupportedError(
                            "LIMIT/OFFSET is not supported with "
                            "select_for_update on this database backend."
                        )
                    nowait = self.query.select_for_update_nowait
                    skip_locked = self.query.select_for_update_skip_locked
                    of = self.query.select_for_update_of
                    no_key = self.query.select_for_no_key_update
                    # If it's a NOWAIT/SKIP LOCKED/OF/NO KEY query but the
                    # backend doesn't support it, raise NotSupportedError to
                    # prevent a possible deadlock.
                    if nowait and not features.has_select_for_update_nowait:
                        raise NotSupportedError(
                            "NOWAIT is not supported on this database backend."
                        )
                    elif skip_locked and not features.has_select_for_update_skip_locked:
                        raise NotSupportedError(
                            "SKIP LOCKED is not supported on this database backend."
                        )
                    elif of and not features.has_select_for_update_of:
                        raise NotSupportedError(
                            "FOR UPDATE OF is not supported on this database backend."
                        )
                    elif no_key and not features.has_select_for_no_key_update:
                        raise NotSupportedError(
                            "FOR NO KEY UPDATE is not supported on this "
                            "database backend."
                        )
                    for_update_part = self.connection.ops.for_update_sql(
                        nowait=nowait,
                        skip_locked=skip_locked,
                        of=self.get_select_for_update_of_arguments(),
                        no_key=no_key,
                    )

                if for_update_part and features.for_update_after_from:
                    result.append(for_update_part)

                if where:
                    result.append("WHERE %s" % where)
                    params.extend(w_params)

                grouping = []
                for g_sql, g_params in group_by:
                    grouping.append(g_sql)
                    params.extend(g_params)
                if grouping:
                    if distinct_fields:
                        raise NotImplementedError(
                            "annotate() + distinct(fields) is not implemented."
                        )
                    order_by = order_by or self.connection.ops.force_no_ordering()
                    result.append("GROUP BY %s" % ", ".join(grouping))
                    if self._meta_ordering:
                        order_by = None
                if having:
                    if not grouping:
                        result.extend(self.connection.ops.force_group_by())
                    result.append("HAVING %s" % having)
                    params.extend(h_params)

            if self.query.explain_info:
                result.insert(
                    0,
                    self.connection.ops.explain_query_prefix(
                        self.query.explain_info.format,
                        **self.query.explain_info.options,
                    ),
                )

            if order_by:
                ordering = []
                for _, (o_sql, o_params, _) in order_by:
                    ordering.append(o_sql)
                    params.extend(o_params)
                order_by_sql = "ORDER BY %s" % ", ".join(ordering)
                # if combinator and features.requires_compound_order_by_subquery:
                #     result = ["SELECT * FROM (", *result, ")", order_by_sql]
                # else:
                result.append(order_by_sql)

            if with_limit_offset:
                if len(result) == 1:
                    result = ["SELECT","* FROM (", *result, ")"]
                result.insert(1,
                    self.connection.ops.limit_offset_sql(
                        self.query.low_mark, self.query.high_mark
                    )
                )

            if for_update_part and not features.for_update_after_from:
                result.append(for_update_part)

            if self.query.subquery and extra_select:
                # If the query is used as a subquery, the extra selects would
                # result in more columns than the left-hand side expression is
                # expecting. This can happen when a subquery uses a combination
                # of order_by() and distinct(), forcing the ordering expressions
                # to be selected as well. Wrap the query in another subquery
                # to exclude extraneous selects.
                sub_selects = []
                sub_params = []
                for index, (select, _, alias) in enumerate(self.select, start=1):
                    if alias:
                        sub_selects.append(
                            "%s.%s"
                            % (
                                self.connection.ops.quote_name("subquery"),
                                self.connection.ops.quote_name(alias),
                            )
                        )
                    else:
                        select_clone = select.relabeled_clone(
                            {select.alias: "subquery"}
                        )
                        subselect, subparams = select_clone.as_sql(
                            self, self.connection
                        )
                        sub_selects.append(subselect)
                        sub_params.extend(subparams)
                return "SELECT %s FROM (%s) subquery" % (
                    ", ".join(sub_selects),
                    " ".join(result),
                ), tuple(sub_params + params)

            return " ".join(result), tuple(params)
        finally:
            # Finally do cleanup - get rid of the joins we created above.
            self.query.reset_refcounts(refcounts_before)

    def get_group_by(self, select, order_by):
        """
        Return a list of 2-tuples of form (sql, params).

        The logic of what exactly the GROUP BY clause contains is hard
        to describe in other words than "if it passes the test suite,
        then it is correct".
        """
        # Some examples:
        #     SomeModel.objects.annotate(Count('somecol'))
        #     GROUP BY: all fields of the model
        #
        #    SomeModel.objects.values('name').annotate(Count('somecol'))
        #    GROUP BY: name
        #
        #    SomeModel.objects.annotate(Count('somecol')).values('name')
        #    GROUP BY: all cols of the model
        #
        #    SomeModel.objects.values('name', 'pk')
        #    .annotate(Count('somecol')).values('pk')
        #    GROUP BY: name, pk
        #
        #    SomeModel.objects.values('name').annotate(Count('somecol')).values('pk')
        #    GROUP BY: name, pk
        #
        # In fact, the self.query.group_by is the minimal set to GROUP BY. It
        # can't be ever restricted to a smaller set, but additional columns in
        # HAVING, ORDER BY, and SELECT clauses are added to it. Unfortunately
        # the end result is that it is impossible to force the query to have
        # a chosen GROUP BY clause - you can almost do this by using the form:
        #     .values(*wanted_cols).annotate(AnAggregate())
        # but any later annotations, extra selects, values calls that
        # refer some column outside of the wanted_cols, order_by, or even
        # filter calls can alter the GROUP BY clause.

        # The query.group_by is either None (no GROUP BY at all), True
        # (group by select fields), or a list of expressions to be added
        # to the group by.
        if self.query.group_by is None:
            return []
        expressions = []
        group_by_refs = set()
        if self.query.group_by is not True:
            # If the group by is set to a list (by .values() call most likely),
            # then we need to add everything in it to the GROUP BY clause.
            # Backwards compatibility hack for setting query.group_by. Remove
            # when we have public API way of forcing the GROUP BY clause.
            # Converts string references to expressions.
            for expr in self.query.group_by:
                if not hasattr(expr, "as_sql"):
                    expr = self.query.resolve_ref(expr)
                if isinstance(expr, Ref):
                    if expr.refs not in group_by_refs:
                        group_by_refs.add(expr.refs)
                        expressions.append(expr.source)
                else:
                    expressions.append(expr)
        # Note that even if the group_by is set, it is only the minimal
        # set to group by. So, we need to add cols in select, order_by, and
        # having into the select in any case.
        selected_expr_positions = {}
        for ordinal, (expr, _, alias) in enumerate(select, start=1):
            if alias:
                selected_expr_positions[expr] = ordinal
            # Skip members of the select clause that are already explicitly
            # grouped against.
            if alias in group_by_refs:
                continue
            expressions.extend(expr.get_group_by_cols())
        if not self._meta_ordering:
            for expr, (sql, params, is_ref) in order_by:
                # Skip references to the SELECT clause, as all expressions in
                # the SELECT clause are already part of the GROUP BY.
                if not is_ref:
                    expressions.extend(expr.get_group_by_cols())
        having_group_by = self.having.get_group_by_cols() if self.having else ()
        for expr in having_group_by:
            expressions.append(expr)
        result = []
        seen = set()
        expressions = self.collapse_group_by(expressions, having_group_by)

        allows_group_by_select_index = (
            self.connection.features.allows_group_by_select_index
        )
        for expr in expressions:
            try:
                sql, params = self.compile(expr)
            except EmptyResultSet:
                continue
            if (
                allows_group_by_select_index
                and (position := selected_expr_positions.get(expr)) is not None
            ):
                sql, params = str(position), ()
            else:
                sql, params = expr.select_format(self, sql, params)
            params_hash = make_hashable(params)
            if (sql, params_hash) not in seen:
                result.append((sql, params))
                seen.add((sql, params_hash))
        return result


class SQLInsertCompiler(compiler.SQLInsertCompiler, SQLCompiler):
    pass


class SQLDeleteCompiler(compiler.SQLDeleteCompiler, SQLCompiler):
    pass


class SQLUpdateCompiler(compiler.SQLUpdateCompiler, SQLCompiler):
    pass


class SQLAggregateCompiler(compiler.SQLAggregateCompiler, SQLCompiler):
    pass



