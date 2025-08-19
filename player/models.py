from django.db import models
from django.contrib.auth import get_user_model
from manager.models import Manager
from school.models import School


User=get_user_model()

class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE ,related_name='player')
    school = models.ForeignKey(School,on_delete=models.CASCADE,related_name='player')
    jersey_number = models.PositiveIntegerField(null=True,blank=True)
    manager = models.ForeignKey(Manager, on_delete=models.SET_NULL, null=True,related_name='player')

    def __str__(self):
        return str(self.user)
