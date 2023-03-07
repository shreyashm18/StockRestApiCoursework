from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class SharesData(models.Model):
    company_name = models.CharField(null=False,blank=False,max_length=225)
    company_symbol = models.CharField(null=False,blank=False,max_length=50)
    no_of_shares = models.IntegerField()
    share_currency = models.CharField(null=False,blank=False,max_length=25)
    share_price = models.FloatField()
    last_updated_date = models.DateField()

    def __str__(self):
        return self.company_name