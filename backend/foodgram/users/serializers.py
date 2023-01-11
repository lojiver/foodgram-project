from djoser.serializers import UserSerializer
from rest_framework import serializers

from .models import User
from lists.models import Subscription


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta():
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        return Subscription.objects.filter(
            author=obj.id, follower=self.context['request'].user
        ).exists()

    def validate_username(self, value):
        username = value.lower()
        if username == 'me':
            raise serializers.ValidationError(
                'Использовать имя "me" в качестве username запрещено'
            )
