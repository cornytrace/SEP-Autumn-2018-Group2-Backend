# Generated by Django 2.1.1 on 2018-10-22 07:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_auto_20181002_1046'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='organization',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
