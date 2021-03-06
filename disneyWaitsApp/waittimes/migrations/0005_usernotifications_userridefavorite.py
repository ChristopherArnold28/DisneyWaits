# Generated by Django 2.1.1 on 2018-10-31 14:00

from django.db import migrations, models
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('waittimes', '0004_todaywaitspredicted'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserNotifications',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('userid', models.IntegerField(db_column='UserId')),
                ('phonenumber', phonenumber_field.modelfields.PhoneNumberField(db_column='PhoneNumber', max_length=128)),
                ('rideid', models.IntegerField(db_column='RideId')),
                ('datestart', models.DateField(db_column='DateStart')),
                ('dateend', models.DateField(db_column='DateEnd')),
            ],
            options={
                'db_table': 'User_Notifications',
            },
        ),
        migrations.CreateModel(
            name='UserRideFavorite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('userid', models.IntegerField(db_column='UserId')),
                ('rideid', models.IntegerField(db_column='RideId')),
            ],
            options={
                'db_table': 'User_Ride_Favorites',
            },
        ),
    ]
