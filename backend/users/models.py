from django.contrib.auth.models import AbstractUser
from django.db import models

from backend.constants import EMAIL_MAX_LENGTH, USER_ROLE_MAX_LENGTH


class User(AbstractUser):
    USER = 'user'
    ADMIN = 'admin'

    ROLE_CHOICES = (
        (USER, 'Пользователь'),
        (ADMIN, 'Администратор'),
    )

    email = models.EmailField('Электронная почта', max_length=EMAIL_MAX_LENGTH,
                              unique=True)
    role = models.CharField('Роль пользователя',
                            max_length=USER_ROLE_MAX_LENGTH,
                            choices=ROLE_CHOICES, default=USER)

    class Meta:
        ordering = ['id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == User.ADMIN

    @property
    def is_user(self):
        return self.role == User.USER

    @property
    def recipes_count(self):
        return self.recipes.count()

    @property
    def get_user_recipes(self):
        return self.recipes.all()
