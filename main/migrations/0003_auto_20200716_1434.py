# Generated by Django 3.0.6 on 2020-07-16 14:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_contact_form'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cinema',
            name='point',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='movie',
            name='point',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='people',
            name='point',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='series',
            name='point',
            field=models.FloatField(default=0),
        ),
    ]
