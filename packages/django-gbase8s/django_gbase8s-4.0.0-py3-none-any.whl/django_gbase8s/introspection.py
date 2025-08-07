from collections import namedtuple
from django.db.backends.base.introspection import BaseDatabaseIntrospection
from django.db.backends.base.introspection import FieldInfo as BaseFieldInfo
from django.db.backends.base.introspection import TableInfo as BaseTableInfo
from django.db.models import Index
from .base import Database

TableInfo = namedtuple("TableInfo", BaseTableInfo._fields + ("comment",))
FieldInfo = namedtuple(
    "FieldInfo", BaseFieldInfo._fields + ("is_autofield", "is_json", "comment", "gbase8s_type_code")
)

class DatabaseIntrospection(BaseDatabaseIntrospection):

    data_types_reverse = {
                Database.DB_TYPE_BINARY_INTEGER: "IntegerField",
                Database.DB_TYPE_DATE: "DateField",
                Database.DB_TYPE_BINARY_DOUBLE: "FloatField",
                Database.DB_TYPE_BLOB: "BinaryField",
                Database.DB_TYPE_CHAR: "CharField",
                Database.DB_TYPE_CLOB: "TextField",
                Database.DB_TYPE_INTERVAL_DS: "DurationField",
                Database.DB_TYPE_NCHAR: "CharField",
                Database.DB_TYPE_NCLOB: "TextField",
                Database.DB_TYPE_NVARCHAR: "CharField",
                Database.DB_TYPE_NUMBER: "IntegerField",
                Database.DB_TYPE_TIMESTAMP: "DateTimeField",
                Database.DB_TYPE_VARCHAR: "CharField",
            }
    
    def get_field_type(self, data_type, description): 
        if data_type == Database.DB_TYPE_BINARY_INTEGER:
            if description.is_autofield:
                if description.gbase8s_type_code == 309:
                    return "BigAutoField"
                else:
                    return "AutoField"
            else:
                if description.gbase8s_type_code in(52, 52 + 256):
                    return "BigIntegerField"
                else:
                    return "IntegerField"
        
        elif data_type == Database.DB_TYPE_NUMBER:
            if description.scale == 0:
                if description.precision == 1:
                    return "BooleanField"
                # elif description.precision > 11:
                #     return "BigIntegerField"
                elif description.internal_size == 51 and description.precision == 50:
                    return "FloatField"
            else:
                return "DecimalField"
        elif data_type == Database.DB_TYPE_TIMESTAMP:
            if description.scale == 0:
                return "DateField"
            else:
                return "DateTimeField"
        return super().get_field_type(data_type, description)
    
    def get_table_list(self, cursor):
        """Return a list of table and view names in the current database."""
        cursor.execute(
            """
            SELECT 
                t1.tabname, 
                t1.tabtype, 
                t2.comments 
            FROM systables as t1
            left join syscomments as t2 on t1.tabname = t2.tabname
            WHERE 
                t1.tabtype in ('T', 'V') 
                and t1.flags = 16384
            """)
        table_list = [
            TableInfo(row[0], {'T': 't', 'V': 'v'}.get(row[1]), row[2].rstrip() if row[2] else None)
            for row in cursor.fetchall()
        ]
        return table_list
    
    def get_table_description(self, cursor, table_name):
        """
        Return a description of the table with the DB-API cursor.description
        interface.
        """
        # get default value
        query_default_sql = """
            select t1.default, t2.colname
            from sysdefaultsexpr t1
            left join syscolumns t2 on (t1.tabid = t2.tabid and t1.colno = t2.colno)
            where t1.tabid = (select tabid from systables where tabname = '{}')
            and t1.type = 'T'
        """.format(table_name)
        cursor.execute(query_default_sql)
        col_default = {colname: default.rstrip() if default else None for default, colname in cursor.fetchall()}
        # get column comment
        query_col_comment = """
            SELECT COLNAME, COMMENTS
            FROM SYSCOLCOMMENTS
            WHERE TABNAME = '{}'
                            """.format(table_name)
        cursor.execute(query_col_comment)
        col_comment = {colname: comment.rstrip() if comment else None for colname, comment in cursor.fetchall()}
        # get column type
        query_col_type = """
            SELECT T1.COLNAME, T1.COLTYPE
            FROM SYSCOLUMNS T1, SYSTABLES T2
            WHERE T1.TABID = T2.TABID
            AND T2.TABNAME = '{}'
                        """.format(table_name)
        cursor.execute(query_col_type)
        col_type= {colname: coltype for colname, coltype in cursor.fetchall()}
        # get description
        query_descriptions_sql = "SELECT * FROM {} WHERE 1=0".format(self.connection.ops.quote_name(table_name))
        cursor.execute(query_descriptions_sql)
        descriptions = []
        for desc in cursor.description:
            field_info = FieldInfo(
                desc[0],    # column name
                desc[1],    # internal type
                desc[3],    # internal size
                desc[2],    # display size
                desc[4] or 0,    # precision
                desc[5] or 0,    # scale
                desc[6],    # null_ok 
                col_default.get(desc[0]),   # default value
                None,   # collation    
                col_type.get(desc[0]) in (262, 309),  # is_autofield
                False,  # unsupport json yield
                col_comment.get(desc[0]),   # comment
                col_type.get(desc[0])   # gbase8s_type_code
            )
            descriptions.append(field_info)
        return descriptions
    
    def get_sequences(self, cursor, table_name, table_fields=()):
        for field_info in self.get_table_description(cursor, table_name):
            if field_info.is_autofield:
                return [{"table": table_name, "column": field_info.name}]
        return []
    
    def get_relations(self, cursor, table_name):
        """
        Return a dictionary of {field_name: (field_name_other_table, other_table)}
        representing all foreign keys in the given table.
        """
        relations = {}
        rows = cursor.execute("""
            select t1.constrname, t1.idxname, t1.tabid, t1.constrid, 
                t2.part1, t2.part2, t2.part3, t2.part4, t2.part5, t2.part6, t2.part7, t2.part8, 
                t2.part9, t2.part10, t2.part11, t2.part12, t2.part13, t2.part14, t2.part15, t2.part16
            from sysconstraints t1
            left join sysindexes t2 on t1.idxname = t2.idxname
            where t1.tabid = (select tabid from systables where tabname=%s)
            and t1.constrtype = 'R'
        """, (table_name, )).fetchall()
        for row in rows:
            tabid = row[2]
            constr_id = row[3]
            cols_pos = [pos for pos in row[4:] if pos]
            colnames = [self._get_column_name_by_tabid_colno(cursor, tabid, pos) for pos in cols_pos]
            referenes_row = cursor.execute("""
                select t4.tabid, t4.tabname, 
                    t3.part1, t3.part2, t3.part3, t3.part4, t3.part5, t3.part6, t3.part7, t3.part8, 
                    t3.part9, t3.part10, t3.part11, t3.part12, t3.part13, t3.part14, t3.part15, t3.part16
                from sysreferences t1, sysconstraints t2, sysindexes t3, systables t4
                where t1.constrid = %s
                and t1.primary = t2.constrid
                and t2.idxname = t3.idxname
                and t3.tabid = t4.tabid      
            """, (constr_id,)).fetchone()
            if not referenes_row:
                continue
            other_table_id = referenes_row[0]
            other_table_name = referenes_row[1]
            cols_pos = [pos for pos in referenes_row[2:] if pos]
            other_col_names = [self._get_column_name_by_tabid_colno(cursor, other_table_id, pos) for pos in cols_pos]
            relations[colnames[0]] = (other_col_names[0], other_table_name)
        return relations

    def _get_column_name_by_tabid_colno(self, cursor, tabid, colno):
        colno = abs(colno)
        cursor.execute("""
            select colname
            from syscolumns
            where tabid = %s
            and colno = %s
        """, (tabid, colno))
        row = cursor.fetchone()
        if not row:
            return None
        return row[0]
    
    def get_primary_key_column(self, cursor, table_name):
        """
        Return the name of the primary key column for the given table.
        """
        columns = self.get_primary_key_columns(cursor, table_name)
        return columns[0] if columns else None
        
    def get_primary_key_columns(self, cursor, table_name):
        cursor.execute(
            """
            select 
            t2.part1, t2.part2, t2.part3, t2.part4, t2.part5, t2.part6, t2.part7, t2.part8, 
            t2.part9, t2.part10, t2.part11, t2.part12, t2.part13, t2.part14, t2.part15, t2.part16
            from sysconstraints t1
            left join sysindexes t2 on t1.idxname = t2.idxname
            where t1.tabid = (select tabid from systables where tabname=%s)
            and t1.constrtype='P'
            """,
            [table_name],
        )
        row = cursor.fetchone()
        if not row:
            return []
        cols_no = [col for col in row if col]
        cursor.execute(
            f"""
            select colname from syscolumns
            where tabid = (select tabid from systables where tabname=%s)
            and colno in ({",".join([str(col) for col in cols_no])})
            """,
            [table_name, ],
        )
        cols_name = [row[0] for row in cursor.fetchall()]
        return cols_name
        
    
    def get_constraints(self, cursor, table_name):
        """
        Retrieve any constraints or keys (unique, pk, fk, check, index) across
        one or more columns.
        """
        constraints = {}
        # find constraints include pk, fk, uq, check

        rows = cursor.execute("""
            select t1.constrname, t1.constrtype, t2.idxname, t1.tabid, t1.constrid, 
                t2.part1, t2.part2, t2.part3, t2.part4, t2.part5, t2.part6, t2.part7, t2.part8, 
                t2.part9, t2.part10, t2.part11, t2.part12, t2.part13, t2.part14, t2.part15, t2.part16
            from sysconstraints t1
            left join sysindexes t2 on t1.idxname = t2.idxname
            where 
                t1.tabid = (select tabid from systables where tabname=%s)
        """, (table_name,)).fetchall()
        rows_index = cursor.execute("""
            select null, null, idxname, tabid, null,
                part1, part2, part3, part4, part5, part6, part7, part8, 
                part9, part10, part11, part12, part13, part14, part15, part16
            from sysindexes 
            where tabid = (select tabid from systables where tabname=%s)
        """, (table_name,)).fetchall()
        all_indexes = []
        rows_all = rows + rows_index
        for row in rows_all:
            if not row[0] and row[2] in all_indexes:    # skip duplicate index
                continue
            constr_name = row[0] or row[2]
            constr_type = row[1]
            idxname = row[2]
            if constr_type != "R":
                all_indexes.append(idxname)
            tabid = row[3]
            constr_id = row[4]
            cols_pos = [pos for pos in row[5:] if pos]
            colnames = [self._get_column_name_by_tabid_colno(cursor, tabid, pos) for pos in cols_pos]
            orders = ['DESC'if pos < 0 else 'ASC' for pos in cols_pos]
            if constr_type == "R":
                referenes_row = cursor.execute("""
                    select t4.tabid, t4.tabname, 
                        t3.part1, t3.part2, t3.part3, t3.part4, t3.part5, t3.part6, t3.part7, t3.part8, 
                        t3.part9, t3.part10, t3.part11, t3.part12, t3.part13, t3.part14, t3.part15, t3.part16
                    from sysreferences t1, sysconstraints t2, sysindexes t3, systables t4
                    where t1.constrid = %s
                    and t1.primary = t2.constrid
                    and t2.idxname = t3.idxname
                    and t3.tabid = t4.tabid      
                """, (constr_id,)).fetchone()
                if not referenes_row:
                    continue
                other_table_id = referenes_row[0]
                other_table_name = referenes_row[1]
                cols_pos = [pos for pos in referenes_row[2:] if pos]
                other_col_names = [self._get_column_name_by_tabid_colno(cursor, other_table_id, pos) for pos in cols_pos]
                foreigen_key = (other_table_name, ) + tuple(other_col_names)
            elif constr_type in ("N", "C"):    # not null or check constraint
                not_null_rows = cursor.execute("""
                    select t2.colname 
                    from syscoldepend t1, syscolumns t2
                    where t1.constrid = %s
                    and t1.tabid = t2.tabid
                    and t1.colno = t2.colno
                    """, (constr_id, )).fetchall()
                colnames = [row[0] for row in not_null_rows]
                foreigen_key = None
            else:
                foreigen_key = None
            constraints[constr_name] = {
                'columns': colnames,
                'primary_key': constr_type == 'P',
                'unique': constr_type == 'U',
                'index': True if idxname and constr_type != 'R' else False,
                'check': constr_type in ('C', 'N'),
                'foreign_key': foreigen_key,
                'type': Index.suffix,
                'orders': orders
            }

        return constraints


    def get_key_columns(self, cursor, table_name):
        relations = []
        rows = cursor.execute("""
            select t1.constrname, t1.idxname, t1.tabid, t1.constrid, 
                t2.part1, t2.part2, t2.part3, t2.part4, t2.part5, t2.part6, t2.part7, t2.part8, 
                t2.part9, t2.part10, t2.part11, t2.part12, t2.part13, t2.part14, t2.part15, t2.part16
            from sysconstraints t1
            left join sysindexes t2 on t1.idxname = t2.idxname
            where t1.tabid = (select tabid from systables where tabname=%s)
            and t1.constrtype = 'R'
        """, (table_name, )).fetchall()
        for row in rows:
            tabid = row[2]
            constr_id = row[3]
            cols_pos = [pos for pos in row[4:] if pos]
            colnames = [self._get_column_name_by_tabid_colno(cursor, tabid, pos) for pos in cols_pos]
            referenes_row = cursor.execute("""
                select t4.tabid, t4.tabname, 
                    t3.part1, t3.part2, t3.part3, t3.part4, t3.part5, t3.part6, t3.part7, t3.part8, 
                    t3.part9, t3.part10, t3.part11, t3.part12, t3.part13, t3.part14, t3.part15, t3.part16
                from sysreferences t1, sysconstraints t2, sysindexes t3, systables t4
                where t1.constrid = %s
                and t1.primary = t2.constrid
                and t2.idxname = t3.idxname
                and t3.tabid = t4.tabid      
            """, (constr_id,)).fetchone()
            if not referenes_row:
                continue
            other_table_id = referenes_row[0]
            other_table_name = referenes_row[1]
            cols_pos = [pos for pos in referenes_row[2:] if pos]
            other_col_names = [self._get_column_name_by_tabid_colno(cursor, other_table_id, pos) for pos in cols_pos]
            # relations[colnames[0]] = (other_col_names[0], other_table_name)
            relations.append((colnames[0], other_table_name, other_col_names[0]))
        return relations
    
    

    

    
    
        