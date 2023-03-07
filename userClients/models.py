from django.contrib.auth.models import User
from django.db import models

class UserClient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(null=False,blank=False,max_length=25)
    is_admin = models.BooleanField(default=False)
    funds = models.FloatField()

    def __str__(self):
        return self.name

class UserSharesData(models.Model):
    username = models.ForeignKey(UserClient, on_delete=models.CASCADE)
    company_name = models.CharField(null=False, blank=False, max_length=225)
    company_symbol = models.CharField(null=False, blank=False, max_length=50)
    shares_qty = models.IntegerField()

    def __str__(self):
        return self.username.name + " " + self.company_symbol

    
