from django.contrib.auth import get_user_model
from rest_framework.generics import CreateAPIView

from user.serializers import UserSerializer


class UserAPIView(CreateAPIView):
    serializer_class = UserSerializer
    queryset = get_user_model().objects.all()