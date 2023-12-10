from news.forms import CommentForm
from yanews import settings


def test_count_news(client, news_list, url_home):
    assert (
        client.get(url_home).context['object_list'].count()
        == settings.NEWS_COUNT_ON_HOME_PAGE
    )


def test_news_order(client, news_list, url_home):
    dates = [
        object.date for object in client.get(url_home).context['object_list']
    ]
    assert dates == sorted(dates, reverse=True)


def test_comments_order(client, comments, url_news_detail):
    response = client.get(url_news_detail)
    assert 'news' in response.context
    dates = [
        comment.created for comment in
        response.context['news'].comment_set.all()
    ]
    assert dates == sorted(dates)


def test_form_unavailable_for_anounymous_user(
        client, url_news_detail
):
    assert 'form' not in client.get(url_news_detail).context


def test_form_available_for_authenticated_user(
        admin_client, url_news_detail
):
    assert isinstance(
        admin_client.get(url_news_detail).context.get('form'),
        CommentForm
    )
