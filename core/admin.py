from django.contrib import admin

from core.models import Client, ClientQueueLock, ClientTransaction


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['__str__']
    search_fields = ['user__first_name', 'user__last_name']


@admin.register(ClientQueueLock)
class ClientQueueLockAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'task_id']
    search_fields = ['client', 'task_id']


@admin.register(ClientTransaction)
class ClientTransactionAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'uid']
    search_fields = ['id', 'uid', 'client']
