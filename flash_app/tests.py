from django.test import Client


def test_main():
    client = Client()
    response = client.get('main/')
    assert response.status_code == 404


def test_view_requires_login():
    client = Client()
    response = client.get('/add_textflashcard')  # jakiś widok wymagający zalogowania
    assert response.status_code == 302  # redirect
    assert response.url == '/accounts/login/?next=/add_textflashcard'  # na jaki adres
