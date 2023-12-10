from http import HTTPStatus

from notes.tests.utils import (
    TestBase,
    URL_HOME,
    URL_LOGIN,
    URL_LOGOUT,
    URL_SIGNUP,
    URL_NOTE_ADD,
    URL_SUCCESS,
    URL_NOTES_LIST,
    URL_NOTE_DETAIL,
    URL_NOTE_EDIT,
    URL_NOTE_DELETE,
)


class TestRoutes(TestBase):

    def test_pages_availability(self):
        for url, parametrized_client, expected_status in [
            [URL_HOME, self.client, HTTPStatus.OK],
            [URL_LOGIN, self.client, HTTPStatus.OK],
            [URL_LOGOUT, self.client, HTTPStatus.OK],
            [URL_SIGNUP, self.client, HTTPStatus.OK],
            [URL_NOTES_LIST, self.author_client, HTTPStatus.OK],
            [URL_NOTE_ADD, self.author_client, HTTPStatus.OK],
            [URL_SUCCESS, self.author_client, HTTPStatus.OK],
            [URL_NOTE_DETAIL, self.author_client, HTTPStatus.OK],
            [URL_NOTE_EDIT, self.author_client, HTTPStatus.OK],
            [URL_NOTE_DELETE, self.author_client, HTTPStatus.OK],
            [URL_NOTE_DETAIL, self.user_client, HTTPStatus.NOT_FOUND],
            [URL_NOTE_EDIT, self.user_client, HTTPStatus.NOT_FOUND],
            [URL_NOTE_DELETE, self.user_client, HTTPStatus.NOT_FOUND],
        ]:
            with self.subTest(
                url=url,
                parametrized_client=parametrized_client,
                expected_status=expected_status
            ):
                self.assertEqual(
                    parametrized_client.get(url).status_code,
                    expected_status
                )

    def test_redirect_for_anonymous_user(self):
        for url, client, url_redirect in (
            (
                URL_NOTE_ADD,
                self.client,
                f'{URL_LOGIN}?next={URL_NOTE_ADD}'
            ),
            (
                URL_NOTE_EDIT,
                self.client,
                f'{URL_LOGIN}?next={URL_NOTE_EDIT}'
            ),
            (
                URL_NOTE_DELETE,
                self.client,
                f'{URL_LOGIN}?next={URL_NOTE_DELETE}'
            ),
            (
                URL_NOTE_DETAIL,
                self.client,
                f'{URL_LOGIN}?next={URL_NOTE_DETAIL}'
            ),
            (
                URL_NOTES_LIST,
                self.client,
                f'{URL_LOGIN}?next={URL_NOTES_LIST}'
            ),
            (
                URL_SUCCESS,
                self.client,
                f'{URL_LOGIN}?next={URL_SUCCESS}'
            )
        ):
            with self.subTest(url=url):
                self.assertRedirects(client.get(url), url_redirect)
