from http import HTTPStatus

from notes.tests import utils


class TestRoutes(utils.TestBase):

    def test_pages_availability(self):
        for url, parametrized_client, expected_status in [
            [utils.URL_HOME, self.client, HTTPStatus.OK],
            [utils.URL_LOGIN, self.client, HTTPStatus.OK],
            [utils.URL_LOGOUT, self.client, HTTPStatus.OK],
            [utils.URL_SIGNUP, self.client, HTTPStatus.OK],
            [utils.URL_NOTES_LIST, self.author_client, HTTPStatus.OK],
            [utils.URL_NOTE_ADD, self.author_client, HTTPStatus.OK],
            [utils.URL_SUCCESS, self.author_client, HTTPStatus.OK],
            [utils.URL_NOTE_DETAIL, self.author_client, HTTPStatus.OK],
            [utils.URL_NOTE_EDIT, self.author_client, HTTPStatus.OK],
            [utils.URL_NOTE_DELETE, self.author_client, HTTPStatus.OK],
            [utils.URL_NOTE_DETAIL, self.user_client, HTTPStatus.NOT_FOUND],
            [utils.URL_NOTE_EDIT, self.user_client, HTTPStatus.NOT_FOUND],
            [utils.URL_NOTE_DELETE, self.user_client, HTTPStatus.NOT_FOUND],
        ]:
            with self.subTest():
                self.assertEqual(
                    parametrized_client.get(url).status_code,
                    expected_status
                )

    def test_redirect_for_anonymous_user(self):
        for url in (
            utils.URL_NOTE_ADD,
            utils.URL_NOTE_EDIT,
            utils.URL_NOTE_DELETE,
            utils.URL_NOTE_DETAIL,
            utils.URL_NOTES_LIST,
            utils.URL_SUCCESS,
        ):
            with self.subTest(url=url):
                self.assertRedirects(
                    self.client.get(url),
                    f'{utils.URL_LOGIN}?next={url}'
                )
