
from decimal import Decimal

from client_transaction import celery_app
from django.db import transaction
from django.db.models import Q

from core.models import ClientQueueLock, ClientTransaction


@celery_app.task(bind=True)
def transaction_processing(self, client_id: int):
    """
    Processing of the first transaction in the queue by date.
    """
    transaction_status = ClientTransaction.TransactionStatus
    # looking for a queue and update it with a single query in the database,
    # this should prevent a race condition
    client_queue = ClientQueueLock.objects \
        .filter(client__id=client_id, task_id__isnull=True) \
        .update(task_id=self.request.id)
    if client_queue == 0:
        return
    q_filter = (
        Q(status=transaction_status.in_queue)
        | Q(status=transaction_status.process)
    )
    client_transaction = ClientTransaction.objects \
        .filter(q_filter, client__id=client_id) \
        .order_by('create_datetime') \
        .first()

    if client_transaction:
        client_transaction.status = transaction_status.process
        client_transaction.save(update_fields=['status'])

        with transaction.atomic():
            client_balance_change = False
            client = client_transaction.client
            if client_transaction.amount > Decimal(0):
                client.balance += client_transaction.amount
                client_balance_change = True
                client_transaction.status = transaction_status.success
            elif abs(client_transaction.amount) <= client.balance:
                client.balance += client_transaction.amount
                client_balance_change = True
                client_transaction.status = transaction_status.success
            else:
                client_transaction.status = transaction_status.canceled
                client_transaction.error_message = 'Not enough money'

            if client_balance_change:
                client.save(update_fields=['balance'])
            client_transaction.save(update_fields=['status'])

    # unlock queue
    ClientQueueLock.objects \
        .filter(client__id=client_id) \
        .update(task_id=None)

    if client_transaction:
        # Repeat the task until all transactions are processed
        transaction_processing.delay(client_id)
