# Generated by Django 2.1.1 on 2018-10-30 15:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('waittimes', '0005_userridefavorite'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserNotifications',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('userid', models.IntegerField(db_column='UserId')),
                ('phonenumber', models.TextField(db_column='PhoneNumber')),
                ('rideid', models.IntegerField(db_column='RideId')),
                ('datestart', models.TextField(db_column='DateStart')),
                ('dateend', models.TextField(db_column='DateEnd')),
            ],
            options={
                'db_table': 'User_Notifications',
            },
        ),
        migrations.AlterField(
            model_name='userridefavorite',
            name='rideid',
            field=models.IntegerField(db_column='RideId'),
        ),
    ]
