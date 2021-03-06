# Generated by Django 3.0.6 on 2020-07-18 08:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contact_Form',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=300)),
                ('last_name', models.CharField(max_length=300)),
                ('email', models.EmailField(max_length=300)),
                ('subject', models.TextField()),
            ],
        ),
        migrations.RemoveField(
            model_name='cinema',
            name='count',
        ),
        migrations.RemoveField(
            model_name='cinema',
            name='point',
        ),
        migrations.RemoveField(
            model_name='movie',
            name='count',
        ),
        migrations.RemoveField(
            model_name='movie',
            name='point',
        ),
        migrations.RemoveField(
            model_name='people',
            name='count',
        ),
        migrations.RemoveField(
            model_name='people',
            name='point',
        ),
        migrations.RemoveField(
            model_name='series',
            name='count',
        ),
        migrations.RemoveField(
            model_name='series',
            name='point',
        ),
        migrations.CreateModel(
            name='Series_Vote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vote', models.IntegerField()),
                ('serial', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Series')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='People_Vote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vote', models.IntegerField()),
                ('people', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.People')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Movies_Vote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vote', models.IntegerField()),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Movie')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Cinema_Vote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vote', models.IntegerField()),
                ('cinema', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Cinema')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
