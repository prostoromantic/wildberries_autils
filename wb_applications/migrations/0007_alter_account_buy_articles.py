# Generated by Django 4.2.3 on 2023-07-24 17:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wb_applications', '0006_alter_account_buy_articles_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='buy_articles',
            field=models.JSONField(default=None, null=True),
        ),
    ]