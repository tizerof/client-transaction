from rest_framework import serializers

from core.models import ClientTransaction


class ClientTransactionSerializer(serializers.ModelSerializer):

    def validate(self, data):
        if data['amount'] < 0:
            client = self.context.get('request').user.client
            if client.balance < abs(data['amount']):
                raise serializers.ValidationError(
                    {'error': 'Not enough money'}
                )
        return data

    def to_representation(self, instance):
        result = super().to_representation(instance)
        if result['error_message'] is None:
            del result['error_message']
        return result

    class Meta:
        model = ClientTransaction
        fields = ['uid', 'amount', 'status', 'error_message',
                  'create_datetime', 'finish_datetime']
        read_only_fields = ['uid', 'status', 'error_message',
                            'create_datetime', 'finish_datetime']
