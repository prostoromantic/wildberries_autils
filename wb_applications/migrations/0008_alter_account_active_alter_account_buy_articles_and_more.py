# Generated by Django 4.2.3 on 2023-07-24 17:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wb_applications', '0007_alter_account_buy_articles'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='active',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='account',
            name='buy_articles',
            field=models.JSONField(default=[], null=True),
        ),
        migrations.AlterField(
            model_name='account',
            name='payment_qr',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='account',
            name='profile_name',
            field=models.IntegerField(default=None),
        ),
    ]
