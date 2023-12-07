from datetime import datetime, timedelta

import pytest

from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News
from yanews import settings


@pytest.fixture
def news_list(db):
    return News.objects.bulk_create(
        News(
            title=f'Новости {index}',
            text='Текст новости',
            date=datetime.today() - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def news(db):
    return News.objects.create(
        title='Заголовок новости',
        text='Текст новости'
    )


@pytest.fixture
def author(django_user_model):
    """Возвращает объект пользователя - автора комментария."""
    return django_user_model.objects.create(username='Автор комментария')


@pytest.fixture
def author_client(author):
    author_client = Client()
    author_client.force_login(author)
    return author_client


@pytest.fixture
def comments(author, news):
    now = timezone.now()
    for index in range(222):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст комментария {index}'
        )
        comment.created = now + timedelta(days=index)
        comment.save()


@pytest.fixture
def comment(author, news):
    return Comment.objects.create(
        text='Комментарий',
        author=author,
        news=news
    )


@pytest.fixture
def form_data():
    return {
        'text': 'Текст комментария'
    }


@pytest.fixture
def url_news_detail(news):
    return reverse('news:detail', args=(news.pk,))


@pytest.fixture
def url_comment_edit(comment):
    return reverse('news:edit', args=(comment.pk,))


@pytest.fixture
def url_comment_delete(comment):
    return reverse('news:delete', args=(comment.pk,))


@pytest.fixture
def url_home():
    return reverse('news:home')


@pytest.fixture
def url_login():
    return reverse('users:login')


@pytest.fixture
def url_logout():
    return reverse('users:logout')


@pytest.fixture
def url_signup():
    return reverse('users:signup')


@pytest.fixture
def url_to_comments(url_news_detail):
    return url_news_detail + '#comments'
