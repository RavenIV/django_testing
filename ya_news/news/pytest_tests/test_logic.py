from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


FORM_DATA = {'text': 'Текст комментария'}


def test_user_can_create_comment(
    author_client, news, author, url_news_detail, url_to_comments
):
    assertRedirects(
        author_client.post(url_news_detail, FORM_DATA),
        url_to_comments,
    )
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == FORM_DATA['text']
    assert new_comment.news == news
    assert new_comment.author == author


def test_anonymous_user_cant_create_comment(
    client, url_news_detail
):
    client.post(url_news_detail, FORM_DATA)
    assert Comment.objects.count() == 0


@pytest.mark.parametrize('bad_word', BAD_WORDS)
def test_user_cant_use_bad_words(author_client, url_news_detail, bad_word):
    assertFormError(
        author_client.post(url_news_detail, {'text': f'Текст {bad_word}'}),
        'form',
        'text',
        errors=WARNING
    )
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(
    author_client, comment, url_comment_edit, url_to_comments, news, author
):
    assertRedirects(
        author_client.post(url_comment_edit, FORM_DATA),
        url_to_comments
    )
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment_from_db.text == FORM_DATA['text']
    assert comment_from_db.news == comment.news
    assert comment_from_db.author == comment.author


def test_user_cant_edit_comment_of_another_user(
    admin_client, comment, url_comment_edit
):
    assert admin_client.post(
        url_comment_edit, FORM_DATA
    ).status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text
    assert comment.author == comment_from_db.author
    assert comment.news == comment_from_db.news


def test_author_can_delete_comment(
    author_client, url_comment_delete, url_to_comments
):
    assertRedirects(
        author_client.post(url_comment_delete),
        url_to_comments
    )
    assert Comment.objects.count() == 0


def test_user_cant_delete_comment_of_another_user(
    admin_client, url_comment_delete, comment
):
    assert admin_client.post(
        url_comment_delete
    ).status_code == HTTPStatus.NOT_FOUND
    comments = Comment.objects.filter(id=comment.id)
    assert comments.exists()
    comment_from_db = comments.get()
    assert comment.text == comment_from_db.text
    assert comment.author == comment_from_db.author
    assert comment.news == comment_from_db.news
