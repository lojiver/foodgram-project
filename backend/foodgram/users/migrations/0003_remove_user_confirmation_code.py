# Generated by Django 3.2.16 on 2022-12-12 11:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20221212_1457'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='confirmation_code',
        ),
    ]
