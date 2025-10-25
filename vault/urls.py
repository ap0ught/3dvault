"""URL configuration for vault app."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from vault.views import CollectionViewSet, VaultFileViewSet

router = DefaultRouter()
router.register(r'collections', CollectionViewSet, basename='collection')
router.register(r'files', VaultFileViewSet, basename='vaultfile')

app_name = 'vault'

urlpatterns = [
    path('api/', include(router.urls)),
]
