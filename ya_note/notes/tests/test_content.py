from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestNotesListPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.user = User.objects.create(username='Другой пользователь')
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)
        cls.note = Note.objects.create(
            title='Заголовок заметки',
            text='Текст заметки',
            author=cls.author
        )

    def test_notes_list_for_different_users(self):
        for user, note_in_list in (
            (self.author_client, True),
            (self.user_client, False)
        ):
            with self.subTest(note_in_list=note_in_list):
                self.assertIs(
                    self.note in user.get(
                        reverse('notes:list')
                    ).context['object_list'],
                    note_in_list,
                    ('Заметка должна отражаться в списке заметок автора '
                     'и не попадать в список других пользователей.')
                )

    def test_notes_pages_contain_form(self):
        for name, args in (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,))
        ):
            with self.subTest(name=name):
                self.assertIn(
                    'form',
                    self.author_client.get(
                        reverse(name, args=args)
                    ).context,
                    ('На страницы создания и редактирования заметки '
                     'должны передаваться формы.')
                )
