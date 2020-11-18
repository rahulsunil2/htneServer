from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    school = models.CharField(max_length=125, null=True)
    grad_year = models.DateField(null=True)
    gender = models.CharField(max_length=1, choices=(("M", "Male"), ("F", "Female")), null=True)
    designation = models.CharField(max_length=25, null=True)
    desc = models.TextField(null=True)

    def __str__(self):  # __unicode__ for Python 2
        return self.user.username


class Team(models.Model):
    team_name = models.CharField(max_length=50, unique=True)
    members = models.ManyToManyField(User)

