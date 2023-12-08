from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()

NOTE_TITLE = 'Заголовок'

NOTE_TEXT = 'Текст заметки'

NOTE_SLUG = 'test_note'

URL_HOME = reverse('notes:home')

URL_LOGIN = reverse('users:login')

URL_LOGOUT = reverse('users:logout')

URL_SIGNUP = reverse('users:signup')

URL_NOTE_ADD = reverse('notes:add')

URL_SUCCESS = reverse('notes:success')

URL_NOTES_LIST = reverse('notes:list')

URL_NOTE_DETAIL = reverse('notes:detail', args=(NOTE_SLUG,))

URL_NOTE_EDIT = reverse('notes:edit', args=(NOTE_SLUG,))

URL_NOTE_DELETE = reverse('notes:delete', args=(NOTE_SLUG,))


class TestBase(TestCase):

    CREATE_NOTE = True
    USE_FORM_DATA = False

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.user = User.objects.create(username='Авторизованный пользователь')
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)
        if cls.CREATE_NOTE:
            cls.note = Note.objects.create(
                title=NOTE_TITLE,
                text=NOTE_TEXT,
                slug=NOTE_SLUG,
                author=cls.author
            )
        if cls.USE_FORM_DATA:
            cls.form_data = {
                'title': NOTE_TITLE,
                'text': NOTE_TEXT,
                'slug': NOTE_SLUG
            }
