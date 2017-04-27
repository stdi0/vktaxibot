from django.db import models

# Create your models here.
class Order(models.Model):
    pos = models.IntegerField(default=0)
    user_id = models.CharField(max_length=30, default='')
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.user_id
