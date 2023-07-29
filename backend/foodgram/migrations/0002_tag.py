# Generated by Django 3.2.16 on 2023-07-25 02:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodgram', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Название тэга')),
                ('color', models.CharField(max_length=7, null=True, verbose_name='Цвет тэга')),
                ('slug', models.SlugField(max_length=200, unique=True, verbose_name='Слаг тэга')),
            ],
        ),
    ]
