from django.db import models
from django.contrib.auth.models import User

class Activate(models.Model):
    username = models.CharField('用户名',max_length=100)
    code = models.CharField('验证码',max_length = 100)
    expiretime = models.DateTimeField('失效时间')


    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "验证码"
        verbose_name_plural = "验证码"
