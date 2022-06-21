from django.contrib.auth.models import User
from django.db import models


class Book(models.Model):
    """ Модель книги """
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    author = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                              related_name='my_books')  # позволяет обращаться ко всем созданным книгам через 'my_books'
    # related_name - псевдоним для поля, по которому у владельца можно получить доступ ко всем созданным им книгам
    readers = models.ManyToManyField(User, through='UserBookRelation',  # readers к User через UserBookRelation
                                     related_name='books')  # related_name(прочитанные)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=None, null=True)

    def __str__(self):
        return f'id {self.id}, {self.name}'


class UserBookRelation(models.Model):
    RATE_CHOICES = (
        (1, 'Bad'),
        (2, 'Fine'),
        (3, 'Good'),
        (4, 'Very Good'),
        (5, 'Amazing')
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    like = models.BooleanField(default=False)
    in_bookmarks = models.BooleanField(default=False)  # Избранное
    rate = models.PositiveSmallIntegerField(choices=RATE_CHOICES, null=True)

    def __str__(self):
        return f'{self.user.username}: {self.book}'

    def save(self, *args, **kwargs):
        from store.logic import set_rating
        creating = not self.pk  # создаём когда нет personal key
        old_rating = self.rate

        super().save(*args, **kwargs)
        new_rating = self.rate
        if old_rating != new_rating or creating:
            set_rating(self.book)