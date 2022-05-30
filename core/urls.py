
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from core.views import ClientTransactionViewSet

router = DefaultRouter()

router.register(
    'transaction', ClientTransactionViewSet, basename='transaction')


urlpatterns = [
    path('v1/', include(router.urls)),
]
