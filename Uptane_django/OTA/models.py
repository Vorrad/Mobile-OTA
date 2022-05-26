from django.db import models
from datetime import datetime
class UserInfo(models.Model):
    time = models.DateTimeField(default=datetime.now)
    name = models.TextField(max_length=64)
    device = models.TextField(max_length=64)
    version = models.TextField(max_length=64)
    reporter = models.TextField(max_length=128)
    file = models.FileField(upload_to='files/', verbose_name=u"文件地址", default='null')
    file_name = models.TextField(max_length=64, default='null')


