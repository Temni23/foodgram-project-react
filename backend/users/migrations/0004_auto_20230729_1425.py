# Generated by Django 3.2.16 on 2023-07-29 07:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_follow'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'ordering': ['-id']},
        ),
        migrations.DeleteModel(
            name='Follow',
        ),
    ]
