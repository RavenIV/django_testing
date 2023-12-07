from http import HTTPStatus
from pytest_django.asserts import assertRedirects, assertFormError

from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


def test_user_can_create_comment(author_client, form_data, news, author):
    url = reverse('news:detail', args=(news.pk,))
    assertRedirects(
        author_client.post(url, form_data),
        (url + '#comments'),
        msg_prefix='Пользователь должен направляться на блок комментариев.'
    )
    assert Comment.objects.count() == 1, (
        'Убедитесь, что авторизованный пользователь '
        'может создать комментарий.'
    )
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.news == news
    assert new_comment.author == author


def test_anonymous_user_cant_create_comment(
    client, form_data, news_pk_for_args
):
    client.post(reverse('news:detail', args=news_pk_for_args), form_data)
    assert Comment.objects.count() == 0, (
        'Убедитесь, что анонимный пользователь не может '
        'создать комментарий.'
    )


def test_user_cant_use_bad_words(author_client, form_data, news_pk_for_args):
    form_data['text'] = f'Текст {BAD_WORDS[0]}'
    assertFormError(
        author_client.post(
            reverse('news:detail', args=news_pk_for_args), form_data
        ),
        'form',
        'text',
        errors=WARNING,
        msg_prefix=(
            'При попытке использовать запрещенные слова в комментарии '
            'форма должна вернуть ошибку.'
        )
    )
    assert Comment.objects.count() == 0, (
        'Убедитесь, что пользователь не может '
        'использовать запрещенные слова в комментарии.'
    )


def test_author_can_edit_comment(
    author_client, form_data, comment, news_pk_for_args
):
    assertRedirects(
        author_client.post(
            reverse('news:edit', args=(comment.pk,)), form_data
        ),
        (reverse('news:detail', args=news_pk_for_args) + '#comments'),
        msg_prefix=(
            'После изменения комментария пользователь должен '
            'быть перенаправлен на страницу новости к блоку комментариев.'
        )
    )
    comment.refresh_from_db()
    assert comment.text == form_data['text'], (
        'Убедитесь, что пользователь может редактировать '
        'свой комментарий.'
    )


def test_user_cant_edit_comment_of_another_user(
    admin_client, form_data, comment
):
    assert admin_client.post(
        reverse('news:edit', args=(comment.pk,)), form_data
    ).status_code == HTTPStatus.NOT_FOUND, (
        'При попытке редактировать чужой комментарий, '
        'пользователь должен получить ошибку 404.'
    )
    assert comment.text == Comment.objects.get(id=comment.id).text, (
        'Убедитесь, что пользователь не может редактировать '
        'чужой комментарий.'
    )


def test_author_can_delete_comment(
    author_client, comment_pk_for_args, news_pk_for_args
):
    assertRedirects(
        author_client.post(reverse('news:delete', args=comment_pk_for_args)),
        (reverse('news:detail', args=news_pk_for_args) + '#comments'),
        msg_prefix=(
            'Пользователь должен быть перенаправлен '
            'на страницу новости к блоку комментариев.'
        )
    )
    assert Comment.objects.count() == 0, (
        'Убедитесь, что пользователь может удалить свой комментарий.'
    )


def test_user_cant_delete_comment_of_another_user(
    admin_client, comment_pk_for_args
):
    assert admin_client.post(
        reverse('news:delete', args=comment_pk_for_args)
    ).status_code == HTTPStatus.NOT_FOUND, (
        'При попытке удалить чужой комментарий '
        'пользователь должен получить ошибку 404.'
    )
    assert Comment.objects.count() == 1, (
        'Комментарий чужого пользователя не должен удаляться.'
    )
