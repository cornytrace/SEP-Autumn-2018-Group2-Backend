# Generated by Django 2.1.1 on 2018-09-26 08:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("coursera", "0009_create_item_peer_assignment_view")]

    operations = [
        migrations.RunSQL(
            sql=[
                """
                DROP VIEW IF EXISTS feedback_course_ratings_view
                """,
                """
                CREATE OR REPLACE VIEW feedback_course_ratings_view
                AS
                SELECT
                MD5(MD5(MD5(MD5(course_id) || eitdigital_user_id) || feedback_system) || feedback_ts) as id,
                course_id,
                eitdigital_user_id,
                feedback_system,
                feedback_rating,
                feedback_max_rating,
                feedback_ts
                FROM
                feedback_course_ratings;
                """,
            ],
            reverse_sql="""
            DROP VIEW feedback_course_ratings_view
            """,
        )
    ]