# Generated by Django 3.0.8 on 2020-08-04 03:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rango', '0010_category_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='slug',
            field=models.SlugField(blank=True, unique=True),
        ),
    ]
