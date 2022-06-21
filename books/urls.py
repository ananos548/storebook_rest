from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework.routers import SimpleRouter

from store.views import BookViewSet, UserBookRelationView

router = SimpleRouter()

router.register(r'book', BookViewSet)
router.register(r'book_relation', UserBookRelationView)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('store.urls')),
    re_path('', include('social_django.urls', namespace='social')),
    # Добавляет опр. urls(например login, disconnect) для auth через соц. сети
    path('__debug__/', include('debug_toolbar.urls')),
]

urlpatterns += router.urls
