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
URL_LOGIN_TO_EDIT_COMMENT = pytest.lazy_fixture('url_login_to_edit_comment')
URL_LOGIN_TO_DELETE_COMMENT = pytest.lazy_fixture(
    'url_login_to_delete_comment'
)


@pytest.mark.parametrize(
    'url, _client, status',
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
    url, _client, status
):
    assert _client.get(url).status_code == status


@pytest.mark.parametrize(
    'url, _client, url_redirect', (
        (URL_COMMENT_DELETE, ANONYMOUS_CLIENT, URL_LOGIN_TO_DELETE_COMMENT),
        (URL_COMMENT_EDIT, ANONYMOUS_CLIENT, URL_LOGIN_TO_EDIT_COMMENT)
    )
)
def test_redirect_for_anonymous_user(_client, url, url_redirect):
    assertRedirects(_client.get(url), url_redirect)
