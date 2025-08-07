"""Tests for SQL analyzer module - ported from TypeScript implementation."""

import pytest
from comprehend_telemetry.sql_analyzer import analyze_sql


class TestSQLAnalyzerBasicOperations:
    """Test basic SQL operations detection."""

    def test_detects_simple_select_from_one_table(self):
        sql = "SELECT * FROM users"
        result = analyze_sql(sql)

        assert result.table_operations == {"users": ["SELECT"]}
        assert result.presentable_query == sql

    def test_detects_insert_into_values(self):
        sql = "INSERT INTO logs (message, level) VALUES ('hi', 'info')"
        result = analyze_sql(sql)

        assert result.table_operations == {"logs": ["INSERT"]}
        assert result.presentable_query == "INSERT INTO logs (message, level) VALUES (...)"

    def test_detects_insert_into_select(self):
        sql = "INSERT INTO archive SELECT * FROM logs"
        result = analyze_sql(sql)

        assert result.table_operations == {
            "archive": ["INSERT"],
            "logs": ["SELECT"]
        }
        assert result.presentable_query == sql

    def test_detects_simple_update(self):
        sql = "UPDATE users SET last_login = NOW() WHERE id = 1"
        result = analyze_sql(sql)

        assert result.table_operations == {"users": ["UPDATE"]}
        assert result.presentable_query == sql

    def test_detects_simple_delete(self):
        sql = "DELETE FROM sessions WHERE expired = true"
        result = analyze_sql(sql)

        assert result.table_operations == {"sessions": ["DELETE"]}
        assert result.presentable_query == sql

    def test_detects_tables_in_delete_using_clause(self):
        sql = """
            DELETE FROM sessions
            USING users
            WHERE sessions.user_id = users.id
          """
        result = analyze_sql(sql)

        assert result.table_operations == {
            "sessions": ["DELETE"],
            "users": ["SELECT"],
        }

        assert "delete" in result.normalized_query.lower()
        assert "sessions" in result.normalized_query.lower()
        assert "using" in result.normalized_query.lower()
        assert "users" in result.normalized_query.lower()
        assert result.presentable_query == sql

    def test_detects_tables_with_aliases_in_from_clause(self):
        sql = """
            SELECT u.id, u.name
            FROM users u
            WHERE u.active = true
          """
        result = analyze_sql(sql)

        assert result.table_operations == {
            "users": ["SELECT"],
        }

        assert "from" in result.normalized_query.lower()
        assert "users" in result.normalized_query.lower()
        assert result.presentable_query == sql

    def test_handles_multiple_operations_on_same_table(self):
        sql = """
          INSERT INTO stats (user_id, value)
          SELECT id, 42 FROM users;
          UPDATE stats SET value = 99 WHERE value < 50;
        """
        result = analyze_sql(sql)

        expected_ops = {"stats": ["INSERT", "UPDATE"], "users": ["SELECT"]}
        assert set(result.table_operations.keys()) == set(expected_ops.keys())
        for table, ops in expected_ops.items():
            assert set(result.table_operations[table]) == set(ops)
        assert result.presentable_query == sql

    def test_detects_tables_in_replace_into_statements(self):
        sql = """
            REPLACE INTO users (id, name) VALUES (1, 'Alice');
          """
        result = analyze_sql(sql)

        assert "users" in result.table_operations
        assert set(result.table_operations["users"]) == {"INSERT", "UPDATE"}

        assert "replace" in result.normalized_query.lower()
        assert "users" in result.normalized_query.lower()
        assert result.presentable_query == """
            REPLACE INTO users (id, name) VALUES (...);
          """

    def test_detects_operation_type_from_merge_when_clause(self):
        sql = """
            MERGE INTO inventory AS t
            USING incoming AS s
            ON t.sku = s.sku
            WHEN MATCHED THEN
              UPDATE SET t.qty = t.qty + s.qty
            WHEN NOT MATCHED THEN
              INSERT (sku, qty) VALUES (s.sku, s.qty);
          """
        result = analyze_sql(sql)

        expected_ops = {"inventory": ["INSERT", "UPDATE"], "incoming": ["SELECT"]}
        assert set(result.table_operations.keys()) == set(expected_ops.keys())
        for table, ops in expected_ops.items():
            assert set(result.table_operations[table]) == set(ops)

        assert "merge" in result.normalized_query.lower()
        assert "inventory" in result.normalized_query.lower()
        assert result.presentable_query == """
            MERGE INTO inventory AS t
            USING incoming AS s
            ON t.sku = s.sku
            WHEN MATCHED THEN
              UPDATE SET t.qty = t.qty + s.qty
            WHEN NOT MATCHED THEN
              INSERT (sku, qty) VALUES (...);
          """

    def test_handles_double_quoted_identifiers(self):
        sql = 'SELECT * FROM "Users" WHERE "Users"."Id" = 42'
        result = analyze_sql(sql)

        assert result.table_operations == {"users": ["SELECT"]}
        assert "users" in result.normalized_query.lower()
        assert result.presentable_query == sql

    def test_handles_backtick_quoted_identifiers_mysql_style(self):
        sql = 'SELECT * FROM `auditLogs` WHERE `eventType` = "login"'
        result = analyze_sql(sql)

        assert result.table_operations == {"auditlogs": ["SELECT"]}
        assert "auditlogs" in result.normalized_query.lower()
        assert result.presentable_query == sql

    def test_handles_bracket_quoted_identifiers_sql_server_style(self):
        sql = "SELECT [userId], [userName] FROM [Accounts]"
        result = analyze_sql(sql)

        assert result.table_operations == {"accounts": ["SELECT"]}
        assert "accounts" in result.normalized_query.lower()
        assert result.presentable_query == sql

    def test_normalizes_quoted_table_names_and_columns_to_lowercase(self):
        sql = 'SELECT "ID", "Email" FROM "Customer"'
        result = analyze_sql(sql)

        assert result.table_operations == {"customer": ["SELECT"]}
        assert "customer" in result.normalized_query.lower()
        assert result.presentable_query == sql

    def test_detects_real_tables_from_subqueries_in_from_clause(self):
        sql = """
            SELECT sq.name
            FROM (
              SELECT name FROM employees WHERE active = true
            ) sq
          """
        result = analyze_sql(sql)

        assert result.table_operations == {
            "employees": ["SELECT"],
        }

        assert "employees" in result.normalized_query.lower()
        assert result.presentable_query == sql

    def test_does_not_treat_from_function_as_table(self):
        sql = """
            SELECT * FROM get_active_users();
          """
        result = analyze_sql(sql)

        assert result.table_operations == {}
        assert "get_active_users" in result.normalized_query.lower()
        assert result.presentable_query == sql

    def test_detects_simple_inner_join(self):
        sql = """
          SELECT * FROM users
          JOIN orders ON users.id = orders.user_id
        """
        result = analyze_sql(sql)

        assert result.table_operations == {
            "users": ["SELECT"],
            "orders": ["SELECT"],
        }

    def test_detects_left_join(self):
        sql = """
          SELECT u.name, o.total
          FROM users u
          LEFT JOIN orders o ON u.id = o.user_id
        """
        result = analyze_sql(sql)

        assert result.table_operations == {
            "users": ["SELECT"],
            "orders": ["SELECT"],
        }

    def test_detects_right_join(self):
        sql = """
          SELECT * FROM payments
          RIGHT JOIN invoices ON payments.invoice_id = invoices.id
        """
        result = analyze_sql(sql)

        assert result.table_operations == {
            "payments": ["SELECT"],
            "invoices": ["SELECT"],
        }

    def test_detects_full_outer_join(self):
        sql = """
          SELECT * FROM logs l
          FULL OUTER JOIN metrics m ON l.time = m.time
        """
        result = analyze_sql(sql)

        assert result.table_operations == {
            "logs": ["SELECT"],
            "metrics": ["SELECT"],
        }

    def test_detects_join_with_subquery_alias(self):
        sql = """
          SELECT * FROM users u
          JOIN (SELECT * FROM events WHERE type = 'login') e ON u.id = e.user_id
        """
        result = analyze_sql(sql)

        assert result.table_operations == {
            "users": ["SELECT"],
            "events": ["SELECT"],
        }

    def test_ignores_subquery_alias_after_join(self):
        sql = """
          SELECT * FROM users
          JOIN (SELECT * FROM sessions) AS s ON users.id = s.user_id
        """
        result = analyze_sql(sql)

        assert result.table_operations == {
            "users": ["SELECT"],
            "sessions": ["SELECT"],
        }

    def test_handles_join_with_quoted_identifiers(self):
        sql = """
          SELECT * FROM "userData"
          JOIN "auditLogs" ON "userData"."id" = "auditLogs"."userId"
        """
        result = analyze_sql(sql)

        assert result.table_operations == {
            "userdata": ["SELECT"],
            "auditlogs": ["SELECT"],
        }

    def test_detects_tables_involved_in_lateral_joins(self):
        sql = """
            SELECT u.id, r.*
            FROM users u
            LEFT JOIN LATERAL (
              SELECT * FROM reports WHERE reports.user_id = u.id ORDER BY created_at DESC LIMIT 1
            ) r ON true
          """
        result = analyze_sql(sql)

        assert result.table_operations == {
            "users": ["SELECT"],
            "reports": ["SELECT"],
        }

        assert "lateral" in result.normalized_query.lower()
        assert "reports" in result.normalized_query.lower()

    def test_collapses_in_clauses_with_values_to_avoid_cardinality_explosion(self):
        sql = "SELECT name FROM users WHERE id IN (1, 2, 3)"
        result = analyze_sql(sql)

        assert result.table_operations == {"users": ["SELECT"]}
        assert "IN(...)" in result.normalized_query
        assert result.presentable_query == "SELECT name FROM users WHERE id IN (...)"

    def test_preserves_and_analyzes_subquery_in_in_clause(self):
        sql = "SELECT * FROM users WHERE id IN (SELECT user_id FROM events)"
        result = analyze_sql(sql)

        assert result.table_operations == {"users": ["SELECT"], "events": ["SELECT"]}
        assert "IN" in result.normalized_query
        assert "SELECT" in result.normalized_query
        assert result.presentable_query == sql

    def test_ignores_ctes_in_table_detection(self):
        sql = """
          WITH recent_orders AS (
            SELECT * FROM orders
          )
          SELECT * FROM recent_orders JOIN users ON users.id = recent_orders.user_id
        """
        result = analyze_sql(sql)

        assert "recent_orders" not in result.table_operations
        assert result.table_operations == {"orders": ["SELECT"], "users": ["SELECT"]}

    def test_handles_multiple_ctes_and_ignores_them_as_tables(self):
        sql = """
            WITH active_users AS (
              SELECT * FROM users WHERE active = true
            ),
            recent_logins AS (
              SELECT * FROM logins WHERE login_time > NOW() - INTERVAL '7 days'
            )
            SELECT au.id, rl.login_time
            FROM active_users au
            JOIN recent_logins rl ON au.id = rl.user_id
            JOIN sessions s ON s.user_id = au.id
          """
        result = analyze_sql(sql)

        assert result.table_operations == {
            "users": ["SELECT"],
            "logins": ["SELECT"],
            "sessions": ["SELECT"],
        }

        assert "active_users" not in result.table_operations
        assert "recent_logins" not in result.table_operations

        # Also check normalization keeps the CTEs in the output
        assert "active_users" in result.normalized_query.lower()
        assert "recent_logins" in result.normalized_query.lower()

    def test_handles_multiple_quoted_ctes_and_real_quoted_table_names(self):
        sql = """
            WITH "ActiveUsers" AS (
              SELECT * FROM "Users" WHERE "Active" = true
            ),
            [RecentLogins] AS (
              SELECT * FROM [Logins] WHERE [LoginTime] > NOW() - INTERVAL '7 days'
            )
            SELECT au."Id", rl."LoginTime"
            FROM "ActiveUsers" au
            JOIN [RecentLogins] rl ON au."Id" = rl."UserId"
            JOIN `Sessions` s ON s.`UserId` = au."Id"
          """
        result = analyze_sql(sql)

        assert result.table_operations == {
            "users": ["SELECT"],
            "logins": ["SELECT"],
            "sessions": ["SELECT"],
        }

        assert "activeusers" not in result.table_operations
        assert "recentlogins" not in result.table_operations

        assert "activeusers" in result.normalized_query.lower()
        assert "recentlogins" in result.normalized_query.lower()
        assert "activeusers" in result.normalized_query.lower()
        assert "sessions" in result.normalized_query.lower()

    def test_handles_recursive_ctes_and_ignores_cte_alias_as_table(self):
        sql = """
            WITH RECURSIVE descendants AS (
              SELECT id, parent_id FROM categories WHERE parent_id IS NULL
              UNION ALL
              SELECT c.id, c.parent_id
              FROM categories c
              JOIN descendants d ON c.parent_id = d.id
            )
            SELECT * FROM descendants;
          """
        result = analyze_sql(sql)

        assert result.table_operations == {
            "categories": ["SELECT"],
        }

        assert "descendants" not in result.table_operations

        # Normalization check (ensure RECURSIVE appears)
        assert "recursive" in result.normalized_query.lower()
        assert "descendants" in result.normalized_query.lower()

    def test_ignores_function_argument_in_extract_when_detecting_tables(self):
        sql = """
          SELECT id, extract('epoch' FROM created) AS time, actor, changes
          FROM transactions
          WHERE transactions.id = $1
        """
        result = analyze_sql(sql)

        assert result.table_operations == {
            "transactions": ["SELECT"]
        }

        # Bonus assertion: normalized query includes EXTRACT(...) intact
        assert "extract" in result.normalized_query.lower()
        assert "created" in result.normalized_query.lower()
        assert result.presentable_query == sql


class TestSQLAnalyzerBulkInsertValues:
    """Test bulk INSERT VALUES cardinality reduction."""

    def test_collapses_single_values_tuple_to_maintain_consistency(self):
        sql = "INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com')"
        result = analyze_sql(sql)

        assert result.table_operations == {"users": ["INSERT"]}
        assert "VALUES(...)" in result.normalized_query
        assert result.presentable_query == "INSERT INTO users (name, email) VALUES (...)"

    def test_collapses_multiple_values_tuples_to_reduce_cardinality(self):
        sql = "INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com'), ('Bob', 'bob@example.com'), ('Charlie', 'charlie@example.com')"
        result = analyze_sql(sql)

        assert result.table_operations == {"users": ["INSERT"]}
        assert "VALUES(...)" in result.normalized_query
        assert result.presentable_query == "INSERT INTO users (name, email) VALUES (...)"

    def test_collapses_multi_line_bulk_insert_values(self):
        sql = """INSERT INTO products (name, price, category_id) VALUES
            ('Laptop', 999.99, 1),
            ('Mouse', 29.99, 2),
            ('Keyboard', 79.99, 2),
            ('Monitor', 299.99, 3)"""
        result = analyze_sql(sql)

        assert result.table_operations == {"products": ["INSERT"]}
        assert "VALUES(...)" in result.normalized_query
        assert result.presentable_query == """INSERT INTO products (name, price, category_id) VALUES
            (...)"""

    def test_handles_bulk_insert_with_different_spacing_and_formatting(self):
        sql = "INSERT INTO logs(timestamp,level,message)VALUES('2023-01-01','info','start'),('2023-01-02','error','failed'),('2023-01-03','info','end')"
        result = analyze_sql(sql)

        assert result.table_operations == {"logs": ["INSERT"]}
        assert "VALUES(...)" in result.normalized_query
        assert result.presentable_query == "INSERT INTO logs(timestamp,level,message)VALUES(...)"

    def test_collapses_replace_into_with_multiple_values_tuples(self):
        sql = "REPLACE INTO cache (key, value, expires) VALUES ('user:1', 'data1', 3600), ('user:2', 'data2', 3600)"
        result = analyze_sql(sql)

        assert "cache" in result.table_operations
        assert set(result.table_operations["cache"]) == {"INSERT", "UPDATE"}
        assert "VALUES(...)" in result.normalized_query
        assert result.presentable_query == "REPLACE INTO cache (key, value, expires) VALUES (...)"

    def test_handles_bulk_insert_with_complex_nested_values(self):
        sql = """INSERT INTO events (data, metadata) VALUES
            ('{"type":"login"}', '{"source":"web","ip":"192.168.1.1"}'),
            ('{"type":"logout"}', '{"source":"mobile","ip":"10.0.0.1"}')"""
        result = analyze_sql(sql)

        assert result.table_operations == {"events": ["INSERT"]}
        assert "VALUES(...)" in result.normalized_query
        assert result.presentable_query == """INSERT INTO events (data, metadata) VALUES
            (...)"""

    def test_preserves_insert_with_subquery_not_values(self):
        sql = "INSERT INTO archive SELECT * FROM logs WHERE created < '2023-01-01'"
        result = analyze_sql(sql)

        assert result.table_operations == {
            "archive": ["INSERT"],
            "logs": ["SELECT"]
        }
        assert result.presentable_query == sql
        assert "VALUES(...)" not in result.normalized_query

    def test_handles_bulk_insert_with_quoted_identifiers(self):
        sql = 'INSERT INTO "UserProfiles" ("firstName", "lastName") VALUES (\'John\', \'Doe\'), (\'Jane\', \'Smith\')'
        result = analyze_sql(sql)

        assert result.table_operations == {"userprofiles": ["INSERT"]}
        assert "VALUES(...)" in result.normalized_query
        assert result.presentable_query == 'INSERT INTO "UserProfiles" ("firstName", "lastName") VALUES (...)'

    def test_handles_bulk_insert_with_mixed_value_types_including_null(self):
        sql = """INSERT INTO metrics (name, value, tags) VALUES
            ('cpu_usage', 85.5, NULL),
            ('memory_usage', 67.2, 'production'),
            ('disk_usage', NULL, 'staging')"""
        result = analyze_sql(sql)

        assert result.table_operations == {"metrics": ["INSERT"]}
        assert "VALUES(...)" in result.normalized_query
        assert result.presentable_query == """INSERT INTO metrics (name, value, tags) VALUES
            (...)"""

    def test_handles_very_large_bulk_insert_cardinality_explosion_scenario(self):
        # Generate a bulk insert with many VALUES tuples to simulate real cardinality issues
        value_tuples = [f"('user{i}', 'user{i}@example.com')" for i in range(100)]
        sql = f"INSERT INTO users (name, email) VALUES {', '.join(value_tuples)}"
        result = analyze_sql(sql)

        assert result.table_operations == {"users": ["INSERT"]}
        assert "VALUES(...)" in result.normalized_query
        assert result.presentable_query == "INSERT INTO users (name, email) VALUES (...)"

        # Ensure the normalized query is much shorter than the original
        assert len(result.normalized_query) < len(sql) // 2

    def test_handles_bulk_insert_with_functions_and_expressions_in_values(self):
        sql = """INSERT INTO audit_log (event_time, user_id, action) VALUES
            (NOW(), 1, 'login'),
            (CURRENT_TIMESTAMP, 2, 'logout'),
            (DATE('2023-01-01'), 3, 'update')"""
        result = analyze_sql(sql)

        assert result.table_operations == {"audit_log": ["INSERT"]}
        assert "VALUES(...)" in result.normalized_query
        assert result.presentable_query == """INSERT INTO audit_log (event_time, user_id, action) VALUES
            (...)"""

    def test_handles_bulk_insert_with_parentheses_in_string_values(self):
        sql = """INSERT INTO comments (text, author) VALUES
            ('This is a comment (with parentheses)', 'user1'),
            ('Another comment (also with parens)', 'user2')"""
        result = analyze_sql(sql)

        assert result.table_operations == {"comments": ["INSERT"]}
        assert "VALUES(...)" in result.normalized_query
        assert result.presentable_query == """INSERT INTO comments (text, author) VALUES
            (...)"""

    def test_preserves_whitespace_before_on_conflict_after_values_clause(self):
        sql = "INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com') ON CONFLICT (email) DO NOTHING"
        result = analyze_sql(sql)

        assert result.table_operations == {"users": ["INSERT"]}
        assert result.presentable_query == "INSERT INTO users (name, email) VALUES (...) ON CONFLICT (email) DO NOTHING"

    def test_preserves_whitespace_before_on_conflict_with_multiple_values_tuples(self):
        sql = "INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com'), ('Bob', 'bob@example.com') ON CONFLICT (email) DO UPDATE SET name = EXCLUDED.name"
        result = analyze_sql(sql)

        assert result.table_operations == {"users": ["INSERT"]}
        assert result.presentable_query == "INSERT INTO users (name, email) VALUES (...) ON CONFLICT (email) DO UPDATE SET name = EXCLUDED.name"