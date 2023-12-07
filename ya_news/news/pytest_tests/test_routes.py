from http import HTTPStatus
import pytest
from pytest_django.asserts import assertRedirects

from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('news_pk_for_args')),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None)
    )
)
def test_pages_availability_for_anonymous_user(client, name, args):
    assert client.get(
        reverse(name, args=args)
    ).status_code == HTTPStatus.OK, (
        f'Страница {name} должна быть доступна анонимному пользователю.'
    )


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
    )
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_availability_for_comment_edit_and_delete(
    parametrized_client, expected_status, name, comment_pk_for_args
):
    assert parametrized_client.get(
        reverse(name, args=comment_pk_for_args)
    ).status_code == expected_status, (
        f'Страница {name} должна быть доступна только автору комментария.'
    )


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_redirect_for_anonymous_user(name, client, comment_pk_for_args):
    login_url = reverse('users:login')
    url = reverse(name, args=comment_pk_for_args)
    assertRedirects(
        client.get(url),
        f'{login_url}?next={url}',
        msg_prefix=(
            f'При открытии страницы {url} анонимный пользователь '
            f'не перенаправляется на страницу авторизации.'
        )
    )
