from django.core import validators
from rest_framework import serializers

from foodgram.models import Ingredient
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=150, required=True,
                                     validators=(
                                         validators.MaxLengthValidator(150),
                                         validators.RegexValidator(
                                             r'^[\w.@+-]+\Z')
                                     ))
    email = serializers.EmailField(max_length=254, required=True)

    class Meta:
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',)
        model = User

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Нельзя выбрать имя me!'
            )
        return value

    def validate(self, attrs):
        user = User.objects.filter(email=attrs.get('email'))
        if user.exists():
            user = user.first()
            if user.username != attrs.get('username'):
                raise serializers.ValidationError(
                    {'Этот email уже используется другим пользователем'}
                )
        user = User.objects.filter(username=attrs.get('username'))
        if user.exists():
            user = user.first()
            if user.email != attrs.get('email'):
                raise serializers.ValidationError(
                    {'Это имя пользователя уже используется'}
                )
        return super().validate(attrs)


class MeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name')
        model = User
        read_only_fields = ('id',)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'measurement_unit',)
        model = Ingredient
