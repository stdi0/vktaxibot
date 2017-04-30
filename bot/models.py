from django.db import models

# Create your models here.
class Order(models.Model):
    pos = models.IntegerField(default=0)
    user_id = models.CharField(max_length=30, default='')
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(default=1)
    #1 - active
    #0 - completed
    #2 - canceled
    #3 - Error code
    city = models.CharField(max_length=30, default=None)
    address_source = models.CharField(max_length=100, default=None)
    address_destination = models.TextField(default=None)
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.user_id
