from datetime import datetime, timedelta
import pytest

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
def news_pk_for_args(news):
    return news.pk,


@pytest.fixture
def author(django_user_model):
    """Возвращает объект пользователя - автора комментария."""
    return django_user_model.objects.create(username='Автор комментария')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def comments(author, news):
    now = timezone.now()
    for index in range(2):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст комментария {index}'
        )
        comment.created = now + timedelta(days=index)
        comment.save()
    return Comment.objects.all()


@pytest.fixture
def comment(author, news):
    return Comment.objects.create(
        text='Комментарий',
        author=author,
        news=news
    )


@pytest.fixture
def comment_pk_for_args(comment):
    return comment.pk,


@pytest.fixture
def form_data():
    return {
        'text': 'Текст комментария'
    }
