from http import HTTPStatus
from pytils.translit import slugify

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note
from notes.tests import utils


form_data = {
    'title': 'Название заметки',
    'text': 'Текст заметки',
    'slug': 'new-note'
}


def request_note_post(client, url):
    return client.post(url, TestNoteCreation.form_data)


class TestNoteCreation(utils.TestBase):

    CREATE_NOTE = False
    USE_FORM_DATA = True

    def test_anonymous_user_cant_create_note(self):
        notes_count = Note.objects.count()
        request_note_post(self.client, utils.URL_NOTE_ADD)
        # self.client.post(utils.URL_NOTE_ADD, self.form_data)
        self.assertEqual(notes_count, Note.objects.count())

    def test_authenticated_user_can_create_note(self):
        notes_count = Note.objects.count()
        self.assertRedirects(
            request_note_post(self.user_client, utils.URL_NOTE_ADD),
            # self.user_client.post(utils.URL_NOTE_ADD, data=self.form_data),
            utils.URL_SUCCESS
        )
        self.assertEqual((notes_count + 1), Note.objects.count())
        note = Note.objects.all().last()
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.user)

    def test_user_cant_use_existing_slug(self):
        Note.objects.create(
            title=self.form_data['title'],
            text=self.form_data['text'],
            slug=self.form_data['slug'],
            author=self.author
        )
        notes_count = Note.objects.count()
        self.assertFormError(
            self.user_client.post(
                utils.URL_NOTE_ADD, data=self.form_data
            ),
            form='form',
            field='slug',
            errors=self.form_data['slug'] + WARNING
        )
        self.assertEqual(notes_count, Note.objects.count())

    def test_empty_slug(self):
        notes_count = Note.objects.count()
        self.form_data.pop('slug')
        self.assertRedirects(
            self.user_client.post(
                utils.URL_NOTE_ADD, data=self.form_data
            ),
            utils.URL_SUCCESS
        )
        self.assertEqual((notes_count + 1), Note.objects.count())
        self.assertEqual(
            Note.objects.all().last().slug,
            slugify(self.form_data['title'])
        )


class TestNoteEditDelete(TestCase):

    NEW_NOTE_TEXT = 'Обновленный текст заметки'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.user = User.objects.create(username='Другой пользователь')
        cls.author_client = Client()
        cls.user_client = Client()
        cls.author_client.force_login(cls.author)
        cls.user_client.force_login(cls.user)
        cls.note = Note.objects.create(
            title=NOTE_TITLE,
            text=NOTE_TEXT,
            slug=NOTE_SLUG,
            author=cls.author
        )
        cls.note_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = {
            'text': cls.NEW_NOTE_TEXT,
            'title': NOTE_TITLE,
        }

    def test_author_can_delete_note(self):
        self.assertRedirects(
            self.author_client.delete(self.delete_url),
            URL_SUCCESS,
            msg_prefix=('После удаления заметки пользователь должен '
                        'направляться на страницу с сообщением '
                        'об успешной операции.')
        )
        self.assertEqual(
            Note.objects.count(),
            0,
            msg='Убедитесь, что автор заметки может её удалить.'
        )

    def test_user_cant_delete_note_of_another_user(self):
        self.assertEqual(
            self.user_client.delete(self.delete_url).status_code,
            HTTPStatus.NOT_FOUND,
            msg=('При попытке удалить чужую заметку '
                 'пользователь должен получить ошибку 404.')
        )
        self.assertEqual(
            Note.objects.count(),
            1,
            msg='Заметка другого пользователя не должна удаляться.'
        )

    def test_author_can_edit_note(self):
        self.assertRedirects(
            self.author_client.post(self.edit_url, data=self.form_data),
            URL_SUCCESS,
            msg_prefix=(f'После изменения заметки пользователь должен '
                        f'направляться на страницу {URL_SUCCESS}.')
        )
        self.note.refresh_from_db()
        self.assertEqual(
            self.note.text,
            self.NEW_NOTE_TEXT,
            msg='Убедитесь, что автор заметки может её изменить.'
        )

    def test_user_cant_edit_note_of_another_user(self):
        self.assertEqual(
            self.user_client.post(
                self.edit_url, data=self.form_data
            ).status_code,
            HTTPStatus.NOT_FOUND,
            msg=('При попытке изменения чужой заметки '
                 'пользователь должен получить ошибку 404.')
        )
        self.note.refresh_from_db()
        self.assertEqual(
            self.note.text,
            NOTE_TEXT,
            msg='Убедитесь, что заметку может изменить только её автор.'
        )
