from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects


pytestmark = pytest.mark.django_db

URL_HOME = pytest.lazy_fixture('url_home')

URL_LOGIN = pytest.lazy_fixture('url_login')

URL_LOGOUT = pytest.lazy_fixture('url_logout')

URL_SIGNUP = pytest.lazy_fixture('url_signup')

URL_NEWS_DETAIL = pytest.lazy_fixture('url_news_detail')

URL_COMMENT_EDIT = pytest.lazy_fixture('url_comment_edit')

URL_COMMENT_DELETE = pytest.lazy_fixture('url_comment_delete')

ANONYMOUS_CLIENT = pytest.lazy_fixture('client')

AUTHOR_CLIENT = pytest.lazy_fixture('author_client')

ADMIN_CLIENT = pytest.lazy_fixture('admin_client')


@pytest.mark.parametrize(
    'url, parametrized_client, expected_status',
    (
        (URL_HOME, ANONYMOUS_CLIENT, HTTPStatus.OK),
        (URL_NEWS_DETAIL, ANONYMOUS_CLIENT, HTTPStatus.OK),
        (URL_LOGIN, ANONYMOUS_CLIENT, HTTPStatus.OK),
        (URL_LOGOUT, ANONYMOUS_CLIENT, HTTPStatus.OK),
        (URL_SIGNUP, ANONYMOUS_CLIENT, HTTPStatus.OK),
        (URL_COMMENT_EDIT, AUTHOR_CLIENT, HTTPStatus.OK),
        (URL_COMMENT_EDIT, ADMIN_CLIENT, HTTPStatus.NOT_FOUND),
        (URL_COMMENT_DELETE, AUTHOR_CLIENT, HTTPStatus.OK),
        (URL_COMMENT_DELETE, ADMIN_CLIENT, HTTPStatus.NOT_FOUND)
    )
)
def test_pages_availability_for_different_users(
    url, parametrized_client, expected_status
):
    assert parametrized_client.get(url).status_code == expected_status


@pytest.mark.parametrize(
    'url',
    (URL_COMMENT_DELETE, URL_COMMENT_EDIT)
)
def test_redirect_for_anonymous_user(url, client, url_login):
    assertRedirects(client.get(url), f'{url_login}?next={url}')
