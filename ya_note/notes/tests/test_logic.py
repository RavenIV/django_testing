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


class TestNoteCreation(utils.TestBase):

    # CREATE_NOTE = False
    
    # @classmethod
    # def setUpTestData(cls):
    #     cls.form_data = {
    #         'title': NOTE_TITLE,
    #         'text': NOTE_TEXT,
    #         'slug': NOTE_SLUG
    #     }
    #     cls.user = User.objects.create(username='Автор заметки')
    #     cls.url_add_note = reverse('notes:add')
    #     cls.user_client = Client()
    #     cls.user_client.force_login(cls.user)

    def test_anonymous_user_cant_create_note(self):
        notes_count = Note.objects.count()
        self.client.post(utils.URL_NOTE_ADD, form_data)
        self.assertEqual(notes_count, Note.objects.count())

    def test_authenticated_user_can_create_note(self):
        self.assertRedirects(
            self.user_client.post(utils.URL_NOTE_ADD, data=form_data),
            utils.URL_SUCCESS
        )
        self.assertEqual(Note.objects.count(), 1)
        note = Note.objects.get()
        for note_field, expected_value in (
            (note.text, form_data['text']),
            (note.title, form_data['title']),
            (note.slug, form_data['slug']),
            (note.author, self.user),
        ):
            with self.subTest(note_field=note_field):
                self.assertEqual(note_field, expected_value)

    def test_user_cant_use_existing_slug(self):
        self.user_client.post(self.url_add_note, data=self.form_data)
        self.assertEqual(
            Note.objects.count(),
            1,
            msg=(
                'Убедитесь, что залогиненный пользователь '
                'может создать заметку.'
            )
        )
        self.assertFormError(
            self.user_client.post(
                self.url_add_note, data=self.form_data
            ),
            form='form',
            field='slug',
            errors=NOTE_SLUG + WARNING,
            msg_prefix=('При указании в форме неуникального '
                        'слага, пользователь должен увидеть предупреждение.')
        )
        self.assertEqual(
            Note.objects.count(),
            1,
            msg=('Если пользователь указал неуникальный слаг '
                 'в форме, заметка не должна создаваться.')
        )

    def test_empty_slug(self):
        self.form_data.pop('slug')
        self.assertRedirects(
            self.user_client.post(
                reverse('notes:add'), data=self.form_data
            ),
            reverse('notes:success'),
            msg_prefix=(
                f'После создания заметки пользователь должен '
                f'перенаправляться на страницу {URL_SUCCESS}'
            )
        )
        self.assertEqual(
            Note.objects.count(),
            1,
            (
                'Убедитесь, что авторизованный пользователь '
                'может создать заметку'
            )
        )
        self.assertEqual(
            Note.objects.get().slug,
            slugify(self.form_data['title']),
            (
                'Если при создании заметки не заполнен slug, '
                'он должен формироваться автоматически'
            )
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
