from django.db import models


# Create your models here.
class Review(models.Model):
    article = models.IntegerField(default=None, null=False)
    imt_id = models.IntegerField(default=None, null=False)
    size = models.CharField(max_length=100, default=None, null=True)
    account = models.IntegerField(default=None, null=False)
    user_name = models.CharField(max_length=25, default=None, null=True)
    review_text = models.CharField(max_length=500, default=None, null=True)
    review_number = models.IntegerField(default=None, null=True)
    review_image = models.ImageField(upload_to='images/', default=None, null=True)
    status = models.BooleanField(default=None, null=False)

    def __str__(self):
        return str(self.article)


class Account(models.Model):
    profile_name = models.IntegerField(default=None, null=False)
    payment_qr = models.BooleanField(default=False, null=False)
    active = models.BooleanField(default=False, null=False)
    buy_articles = models.JSONField(default=list, null=True, blank=True)


class Address(models.Model):
    address_id = models.IntegerField(default=None, null=False)
    address_name = models.CharField(max_length=300, null=False)


class Ransoms(models.Model):
    profile_name = models.IntegerField(default=None, null=False)
    article = models.IntegerField(default=None, null=False)
    ransom_date = models.DateTimeField(default=None, null=False)
    address = models.CharField(max_length=200, default=None, null=False)
