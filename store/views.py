from django.db.models import Count, Case, When, Avg
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from store.models import Book, UserBookRelation
from store.permissions import IsOwnerOrStaffOrReadOnly
from store.serializers import BookSerializer, UserBookrelationSerializer


class BookViewSet(ModelViewSet):
    queryset = books = Book.objects.all().annotate(
        annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
        # Обращаемся к UserBookRelation к объекту like(userbookrelation__like)
    ).select_related('owner').prefetch_related('readers').order_by('id')  # Какие поля модели будут передоваться
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend,
                       OrderingFilter,
                       SearchFilter,
                       ]  # Поиск в django используется мин. для 2 полей(для одного достаточно filter)
    filter_fields = ['price']
    search_fields = ['name', 'author']
    ordering_fields = ['price', 'author']
    permission_classes = [IsOwnerOrStaffOrReadOnly]

    def perform_create(self, serializer):
        """ Присвоение книги владельца  """
        serializer.validated_data['owner'] = self.request.user
        serializer.save()


class UserBookRelationView(UpdateModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    queryset = UserBookRelation.objects.all()
    serializer_class = UserBookrelationSerializer
    lookup_field = 'book'

    def get_object(self):
        obj, _ = UserBookRelation.objects.get_or_create(user=self.request.user,
                                                        book_id=self.kwargs['book'])  # _ = created(создан или найден)
        return obj


def auth(request):
    return render(request, 'oauth.html')
