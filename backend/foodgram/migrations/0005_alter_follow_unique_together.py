# Generated by Django 3.2.16 on 2023-07-27 08:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodgram', '0004_auto_20230727_1510'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='follow',
            unique_together=set(),
        ),
    ]
