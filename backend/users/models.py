from django.contrib.auth.models import AbstractUser
from django.core import validators
from django.db import models


class User(AbstractUser):
    username = models.CharField(
        blank=False,
        verbose_name='Логин',
        max_length=150,
        unique=True,
        validators=[validators.RegexValidator(
            regex=r'^[\w.@+-]+$',
            message='Введите допустимое имя пользователя.',
            code='invalid')]
    )
    email = models.EmailField(
        blank=False,
        verbose_name='email',
        max_length=254,
        unique=True)
    first_name = models.CharField(
        blank=False,
        verbose_name='Имя',
        max_length=150)
    last_name = models.CharField(
        blank=False,
        verbose_name='Фамилия',
        max_length=150)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ['username']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_admin(self):
        return self.is_staff

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = "Подписаться на автора"
        verbose_name_plural = "Подписки автора"
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_follow')
        ]

    def __str__(self):
        return f'Пользователь:{self.user} подписался на {self.author}'
