from http import client
from django.db import transaction
from rest_framework.generics import get_object_or_404, RetrieveAPIView
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from core.models import Client, ClientTransaction
from core.serializers import ClientTransactionSerializer
from core.tasks import transaction_processing


class ClientViewSet(RetrieveAPIView):
    queryset = ClientTransaction.objects.all()
    serializer_class = ClientTransactionSerializer
    lookup_field = 'uid'

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        self.client = get_object_or_404(
            Client.objects.select_for_update(), user=self.request.user)
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(client=self.client)
        transaction.on_commit(
            lambda: transaction_processing.delay(self.client.id))


class CreateRetrieveViewset(CreateModelMixin,
                            RetrieveModelMixin,
                            GenericViewSet):
    pass


class ClientTransactionViewSet(CreateRetrieveViewset):
    queryset = ClientTransaction.objects.all()
    serializer_class = ClientTransactionSerializer
    lookup_field = 'uid'

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        self.client = get_object_or_404(
            Client.objects.select_for_update(), user=self.request.user)
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(client=self.client)
        transaction.on_commit(
            lambda: transaction_processing.delay(self.client.id))
