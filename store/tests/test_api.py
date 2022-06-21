import json

from django.contrib.auth.models import User
from django.db.models import Count, Case, When, Avg
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase

from store.models import Book, UserBookRelation
from store.serializers import BookSerializer


class BooksApiTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(username='test_user')
        self.book_1 = Book.objects.create(name='Test book1', price=225, author='Author 1', owner=self.user)
        self.book_2 = Book.objects.create(name='Test book2', price=125, author='Author 5')
        self.book_3 = Book.objects.create(name='Test book3', price=225, author='Author 1')
        self.book_4 = Book.objects.create(name='Test book3', price=225, author='Author 1')
        UserBookRelation.objects.create(user=self.user, book=self.book_4, like=True, rate=5)

    def test_get(self):
        url = reverse('book-list')
        response = self.client.get(url)
        books = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1)))
        ).order_by('id')
        serializer_data = BookSerializer(books, many=True).data  # Даёт понять, что надо сравнить все объекты, а не один
        self.assertEqual(status.HTTP_200_OK, response.status_code)  # Сравниваем Http статусы
        self.assertEqual(serializer_data, response.data)  # Сравниваем данные из serializer_data и response.data
        self.assertEqual(serializer_data[3]['rating'], '5.00')
        self.assertEqual(serializer_data[3]['annotated_likes'], 1)

    def test_create(self):
        """ Тест create """
        self.assertEqual(4, Book.objects.all().count())  # Проверяем, что книг всего 3
        url = reverse('book-list')
        data = {"name": "Python3",
                "price": 150,
                "author": "Mark Summerfield"
                }
        json_data = json.dumps(data)  # Переводим data в json формат и отправляем
        self.client.force_login(self.user)
        response = self.client.post(url, data=json_data,
                                    content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(5, Book.objects.all().count())  # проверям, что книга действительно создалась => их стало 4
        self.assertEqual(self.user, Book.objects.last().owner)

    def test_update(self):
        """ Тест update """
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {"name": self.book_1.name,
                "price": 510,
                "author": self.book_1.author
                }
        json_data = json.dumps(data)  # Переводим data в json формат
        self.client.force_login(self.user)
        response = self.client.put(url, data=json_data,
                                   content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        # self.book_1 = Book.objects.get(id=self.book_1.id)  # book1 указан в Setup => Он обновляется только в бд
        self.book_1.refresh_from_db()  # Аналог пред. строки
        self.assertEqual(510, self.book_1.price)

    def test_update_not_owner(self):
        """ Тест на редакт книги НЕ владельца книги """
        self.user2 = User.objects.create(username='test_user2')  # Создаём Не владельца книги
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {"name": self.book_1.name,
                "price": 510,
                "author": self.book_1.author
                }
        json_data = json.dumps(data)  # Переводим data в json формат
        self.client.force_login(self.user2)  # Не владелец
        response = self.client.put(url, data=json_data,
                                   content_type='application/json')
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual({'detail': ErrorDetail(string='You do not have permission to perform this action.',
                                                code='permission_denied')},
                         response.data)
        # self.book_1 = Book.objects.get(id=self.book_1.id)  # book1 указан в Setup => Он обновляется только в бд
        self.book_1.refresh_from_db()  # Аналог пред. строки
        self.assertEqual(225, self.book_1.price)

    def test_update_staff(self):
        """ Тест на редакт книги НЕ владельца книги, но админ/персонал могут  """
        self.user2 = User.objects.create(username='test_user2', is_staff=True)  # Создаём Не владельца книги
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {"name": self.book_1.name,
                "price": 510,
                "author": self.book_1.author
                }
        json_data = json.dumps(data)  # Переводим data в json формат
        self.client.force_login(self.user2)  # Не владелец
        response = self.client.put(url, data=json_data,
                                   content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # self.book_1 = Book.objects.get(id=self.book_1.id)  # book1 указан в Setup => Он обновляется только в бд
        self.book_1.refresh_from_db()  # Аналог пред. строки
        self.assertEqual(510, self.book_1.price)


class BooksRelationTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(username='test_user')
        self.user2 = User.objects.create(username='test_user2')
        self.book_1 = Book.objects.create(name='Test book 1', price=25,
                                          author='Author 1')
        self.book_2 = Book.objects.create(name='Test book 2', price=25,
                                          author='Author 2')

    def test_patch(self):
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))
        data = {
            'like': True
        }

        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data,
                                     content_type='application/json')  # patch почти как put
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relations = UserBookRelation.objects.get(user=self.user,
                                                 book=self.book_1)
        self.assertTrue(relations.like)

        data = {
            'in_bookmarks': True
        }
        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data,
                                     content_type='application/json')
        relations = UserBookRelation.objects.get(user=self.user,
                                                 book=self.book_1)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertTrue(relations.in_bookmarks)

    def test_rate(self):
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))
        data = {
            'rate': 3,
        }

        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data,
                                     content_type='application/json')  # patch почти как put
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relations = UserBookRelation.objects.get(user=self.user,
                                                 book=self.book_1)
        self.assertEqual(3, relations.rate)

    def test_rate_wrong(self):
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))
        data = {
            'rate': 6,
        }

        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data,
                                     content_type='application/json')  # patch почти как put
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code, response.data)
