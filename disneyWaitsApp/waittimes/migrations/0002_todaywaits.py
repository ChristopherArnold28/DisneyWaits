# Generated by Django 2.1.1 on 2018-09-28 22:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('waittimes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TodayWaits',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(db_column='Date')),
                ('time', models.TextField(db_column='Time')),
                ('wait', models.IntegerField(db_column='Wait')),
            ],
            options={
                'db_table': 'Ride_Waits_Today',
                'managed': False,
            },
        ),
    ]
