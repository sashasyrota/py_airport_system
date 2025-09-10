from django.urls import path

from user.views import UserAPIView

app_name = "user"

urlpatterns = [
    path("register/", UserAPIView.as_view(), name="create")
]