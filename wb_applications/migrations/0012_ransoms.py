# Generated by Django 4.2.3 on 2023-07-24 17:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wb_applications', '0011_alter_account_buy_articles'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ransoms',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile_name', models.IntegerField(default=None)),
                ('article', models.IntegerField(default=None)),
                ('ransom_date', models.DateTimeField(default=None)),
            ],
        ),
    ]
