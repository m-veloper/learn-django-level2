from django.db import models

class User(models.Model):
    email = models.EmailField()
    password = models.CharField(max_length=100, verbose_name='비밀번호')
    register_date = models.DateTimeField(auto_now_add=True, verbose_name='등록일')

    def __str__(self):
        return self.email

    class Meta:
        db_table = 'user'
        verbose_name = '사용자'
        verbose_name_plural = '사용자'
