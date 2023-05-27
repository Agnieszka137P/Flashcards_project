from django.contrib.auth.models import User
import pytest


@pytest.fixture
def user():
    user = User.objects.create_user(username="user", password="")
    return user
