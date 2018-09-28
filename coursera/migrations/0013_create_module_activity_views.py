# Generated by Django 2.1.1 on 2018-09-28 11:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("coursera", "0012_create_leavers_per_module_view")]

    operations = [
        migrations.RunSQL(
            [
                """
                CREATE MATERIALIZED VIEW
                    module_first_activity_view
                AS
                SELECT DISTINCT ON (module_id, eitdigital_user_id)
                    MD5(MD5(module_id) || eitdigital_user_id)::varchar(50) as id,
                    module_id,
                    eitdigital_user_id,
                    course_progress_ts
                FROM
                    course_branch_modules_view
                    JOIN course_branch_lessons_view USING (module_id)
                    JOIN course_branch_items_view USING (lesson_id)
                    JOIN course_progress_view USING (item_id)
                ORDER BY
                    module_id,
                    eitdigital_user_id,
                    course_progress_ts ASC
                """,
                """
                CREATE UNIQUE INDEX ON module_first_activity_view (id)
                """,
                """
                CREATE UNIQUE INDEX ON module_first_activity_view (module_id, eitdigital_user_id)
                """,
                """
                CREATE INDEX ON module_first_activity_view (course_progress_ts)
                """,
            ],
            reverse_sql="DROP MATERIALIZED VIEW IF EXISTS module_first_activity_view",
        ),
        migrations.RunSQL(
            [
                """
                CREATE MATERIALIZED VIEW
                    module_last_activity_view
                AS
                SELECT DISTINCT ON (module_id, eitdigital_user_id)
                    MD5(MD5(module_id) || eitdigital_user_id)::varchar(50) as id,
                    module_id,
                    eitdigital_user_id,
                    course_progress_ts
                FROM
                    course_branch_modules_view
                    JOIN course_branch_lessons_view USING (module_id)
                    JOIN course_branch_items_view USING (lesson_id)
                    JOIN course_progress_view USING (item_id)
                ORDER BY
                    module_id,
                    eitdigital_user_id,
                    course_progress_ts DESC
                """,
                """
                CREATE UNIQUE INDEX ON module_last_activity_view (id)
                """,
                """
                CREATE UNIQUE INDEX ON module_last_activity_view (module_id, eitdigital_user_id)
                """,
                """
                CREATE INDEX ON module_last_activity_view (course_progress_ts)
                """,
            ],
            reverse_sql="DROP MATERIALIZED VIEW IF EXISTS module_last_activity_view",
        ),
    ]