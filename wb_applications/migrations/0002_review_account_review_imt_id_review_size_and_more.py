# Generated by Django 4.2.3 on 2023-07-23 18:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wb_applications', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='account',
            field=models.IntegerField(default=None),
        ),
        migrations.AddField(
            model_name='review',
            name='imt_id',
            field=models.IntegerField(default=None),
        ),
        migrations.AddField(
            model_name='review',
            name='size',
            field=models.CharField(default=None, max_length=100),
        ),
        migrations.AlterField(
            model_name='review',
            name='article',
            field=models.IntegerField(default=None),
        ),
        migrations.AlterField(
            model_name='review',
            name='review_image',
            field=models.ImageField(default=None, upload_to='images/'),
        ),
        migrations.AlterField(
            model_name='review',
            name='review_number',
            field=models.IntegerField(default=None),
        ),
        migrations.AlterField(
            model_name='review',
            name='review_text',
            field=models.CharField(default=None, max_length=500),
        ),
        migrations.AlterField(
            model_name='review',
            name='status',
            field=models.BooleanField(default=None),
        ),
        migrations.AlterField(
            model_name='review',
            name='user_name',
            field=models.CharField(default=None, max_length=25),
        ),
    ]
