from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects

URL_EDIT_DELETE: tuple[str] = ('news:edit', 'news:delete')


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('pk_for_args')),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None)
    )
)
def test_pages_availability_for_anonymous_user(client, name, args):
    """
    Доступность страниц для анонимного пользователя.

    Домашняя, отдельная новость, логин, логаут, регистрация.
    """
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name',
    URL_EDIT_DELETE,
)
def test_availability_for_comment_edit_and_delete(
    parametrized_client, expected_status, name, pk_for_args
):
    """
    Доступность страниц для авторизованного пользователя.

    Удаление и редактирования своих / чужих комментариев.
    """
    url = reverse(name, args=pk_for_args)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name',
    URL_EDIT_DELETE,
)
def test_redirect_for_anonymous_client(name, client, pk_for_args):
    """Редирект анонимного пользователя."""
    login_url = reverse('users:login')
    url = reverse(name, args=pk_for_args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
