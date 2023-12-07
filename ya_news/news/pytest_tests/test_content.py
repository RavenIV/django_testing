import pytest

from django.urls import reverse

from yanews import settings


HOME_URL = reverse('news:home')


@pytest.mark.usefixtures('news_list')
def test_count_news(client):
    assert len(
        client.get(HOME_URL).context['object_list']
    ) == settings.NEWS_COUNT_ON_HOME_PAGE, (
        f'Количество новостей на домашней странице '
        f'должно составлять {settings.NEWS_COUNT_ON_HOME_PAGE}.'
    )


@pytest.mark.usefixtures('news_list')
def test_news_order(client):
    all_dates = [
        object.date for object in client.get(HOME_URL).context['object_list']
    ]
    assert all_dates == sorted(all_dates, reverse=True), (
        'Новости на домашней странице '
        'должны быть отсортированы от новых к старым.'
    )


@pytest.mark.usefixtures('comments')
def test_comments_order(news_pk_for_args, client):
    response = client.get(reverse('news:detail', args=news_pk_for_args))
    assert 'news' in response.context
    all_comments = response.context['news'].comment_set.all()
    assert all_comments[0].created < all_comments[1].created, (
        'Комментарии должны быть отсортированы от старых к новым.'
    )


@pytest.mark.parametrize(
    'parametrized_client, form_in_context',
    (
        (pytest.lazy_fixture('client'), False),
        (pytest.lazy_fixture('admin_client'), True)
    )
)
def test_form_availability_for_different_users(
    parametrized_client, form_in_context, news_pk_for_args
):
    response = parametrized_client.get(
        reverse('news:detail', args=news_pk_for_args)
    )
    assert ('form' in response.context) is form_in_context, (
        'Форма комментария должна быть доступна '
        'только авторизованному пользователю.'
    )
