from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USER = 'user'
    ADMIN = 'admin'

    ROLE_CHOICES = (
        (USER, 'Пользователь'),
        (ADMIN, 'Администратор'),
    )

    email = models.EmailField("Электронная почта", max_length=254, unique=True)
    username = models.CharField("Логин", max_length=150, unique=True)
    first_name = models.CharField("Имя", max_length=150)
    last_name = models.CharField("Фамилия", max_length=150)
    password = models.CharField("Пароль", max_length=150)
    confirmation_code = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Код подтверждения',
    )
    created = models.DateTimeField(
        'Дата создания пользователя', auto_now_add=True)

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == User.ADMIN

    @property
    def is_user(self):
        return self.role == User.USER
