import uuid
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class Client(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='client')
    balance = models.DecimalField(
        _('Balance'), max_digits=32, decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))])

    class Meta:
        verbose_name = _('Client')
        verbose_name_plural = _('Clients')

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class ClientQueueLock(models.Model):
    """
    Status of the client transaction queue
    """
    client = models.OneToOneField(
        Client, on_delete=models.CASCADE, related_name='queue_lock')
    task_id = models.CharField(max_length=36, null=True, blank=True)

    class Meta:
        verbose_name = _('Client Queue Lock')
        verbose_name_plural = _('Client Queue Locks')

    def __str__(self):
        return f'Queue {self.client}'


class ClientTransaction(models.Model):
    class TransactionStatus(models.TextChoices):
        in_queue = 'in_queue', _('In the queue')
        process = 'process', _('Processing')
        success = 'success', _('Succeed')
        canceled = 'canceled', _('Cancelled')

    client = models.ForeignKey(
        Client, on_delete=models.PROTECT, related_name='transactions')
    uid = models.UUIDField(
        unique=True, editable=False, default=uuid.uuid4, db_index=True)
    amount = models.DecimalField(
        _('Amount'), max_digits=32, decimal_places=2)
    status = models.CharField(
        _('Status'), max_length=8,
        choices=TransactionStatus.choices,
        default=TransactionStatus.in_queue)
    create_datetime = models.DateTimeField(
        _('Date Time create'), default=timezone.now)
    finish_datetime = models.DateTimeField(null=True, blank=True)
    error_message = models.CharField(
        _('Error message'), max_length=100, null=True, blank=True)

    class Meta:
        verbose_name = _('Transaction')
        verbose_name_plural = _('Transactions')
        ordering = ['-create_datetime']

    def __str__(self):
        return f'Transaction {self.client} {self.id}'

    def save(self, update_fields=None, **kwargs) -> None:
        if self.status in (self.TransactionStatus.success,
                           self.TransactionStatus.canceled):
            self.finish_datetime = timezone.now()
            if update_fields:
                update_fields.append('finish_datetime')
        return super().save(**kwargs)


@receiver(post_save, sender=User)
def client_create(sender, instance=None, created=False, **kwargs):
    if created:
        client = Client.objects.create(user=instance, balance=Decimal('0'))
        ClientQueueLock.objects.create(client=client)
