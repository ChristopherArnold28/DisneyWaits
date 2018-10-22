# Generated by Django 2.1.1 on 2018-10-10 17:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('waittimes', '0002_todaywaits'),
    ]

    operations = [
        migrations.CreateModel(
            name='RideCurrentStatus',
            fields=[
                ('rideid', models.ForeignKey(db_column='RideId', on_delete=django.db.models.deletion.DO_NOTHING, primary_key=True, serialize=False, to='waittimes.Ride')),
                ('status', models.TextField(db_column='Status')),
                ('fastpass', models.TextField(db_column='FastPassAvailable')),
            ],
            options={
                'db_table': 'Ride_Current_Status',
                'managed': False,
            },
        ),
    ]