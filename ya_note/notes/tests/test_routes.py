from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.reader = User.objects.create(
            username='Авторизованный пользователь'
        )
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='test_note',
            author=cls.author
        )

    def test_pages_availability_for_all_users(self):
        for name in (
            'notes:home',
            'users:login',
            'users:logout',
            'users:signup',
        ):
            with self.subTest():
                self.assertEqual(
                    self.client.get(reverse(name)).status_code,
                    HTTPStatus.OK,
                    msg=(f'Анонимному пользователю должна '
                         f'быть доступна страница {name}')
                )

    def test_pages_availability_for_authenticated_users(self):
        self.client.force_login(self.author)
        for name in ('notes:list', 'notes:success', 'notes:add'):
            with self.subTest(name=name):
                self.assertEqual(
                    self.client.get(reverse(name)).status_code,
                    HTTPStatus.OK,
                    msg=(f'Авторизованному пользователю '
                         f'должна быть доступна страница {name}')
                )

    def test_notes_availability(self):
        for user, status in (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND)
        ):
            self.client.force_login(user)
            for name in ('notes:detail', 'notes:edit', 'notes:delete'):
                with self.subTest(name=name, user=user):
                    self.assertEqual(
                        self.client.get(
                            reverse(name, args=(self.note.slug,))
                        ).status_code,
                        status,
                        msg=(f'Страница {name} должна быть'
                             f'доступна автору заметки '
                             f'и не доступна другим пользователям')
                    )

    def test_redirect_for_anonymous_user(self):
        login_url = reverse('users:login')
        for name, args in (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
            ('notes:detail', (self.note.slug,)),
            ('notes:list', None),
            ('notes:success', None),
        ):
            with self.subTest(name=name, args=args):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertRedirects(
                    response,
                    f'{login_url}?next={url}',
                    msg_prefix=(
                        f'При открытии страницы {url} анонимный пользователь '
                        f'не перенаправляется на страницу авторизации'
                    )
                )
