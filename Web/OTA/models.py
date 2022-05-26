from django.db import models
from datetime import datetime
class UserInfo(models.Model):
    time = models.DateTimeField(default=datetime.now)
    name = models.TextField(max_length=64)
    device = models.TextField(max_length=64)
    version = models.TextField(max_length=64)
    reporter = models.TextField(max_length=128)


