from django.db import models

# Create your models here.
class Order(models.Model):
    pos = models.IntegerField(default=0)
    user_id = models.CharField(max_length=30, default='')
    message = models.TextField(default=None)
    date = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(default=1)
    #1 - active
    #0 - completed
    #2 - canceled
    #3 - Error code
    city = models.CharField(max_length=30, default=None, null=True)
    phone = models.CharField(max_length=20, default=None, null=True)
    active = models.BooleanField(default=False)
    tmp = models.CharField(max_length=100)
    #canceled = models.BooleanField(default=False)

    def __str__(self):
        return self.user_id
