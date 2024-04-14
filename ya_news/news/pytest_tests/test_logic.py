from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

COMMENT_TEXT: str = 'Текст комментария'
FORM_DATA: dict[str, str] = {'text': COMMENT_TEXT}
NEW_COMMENT_TEXT: str = 'Обновлённый комментарий'
NEW_FORM_DATA: dict[str, str] = {'text': NEW_COMMENT_TEXT}
COMMENTS_REDIRECT: str = '#comments'
COMMENT_ADD_TRUE: int = 1
COMMENT_ADD_DELETE_FALSE: int = 0
COMMENT_DELETE_TRUE: int = -1
COMMENT_EDIT_TRUE: int = 0

pytestmark = pytest.mark.django_db


def test_anonymous_user_cant_create_comment(client, news):
    """Анонимный пользователь не может отправить комментарий."""
    url = reverse('news:detail', args=(news.id,))
    comments_before = Comment.objects.count()
    client.post(url, data=FORM_DATA)
    comments_after = Comment.objects.count()
    assert (comments_after - comments_before) == COMMENT_ADD_DELETE_FALSE


def test_user_can_create_comment(author, author_client, news):
    """Авторизованный пользователь может отправить комментарий."""
    url = reverse('news:detail', args=(news.id,))
    comments_before = Comment.objects.count()
    response = author_client.post(url, data=FORM_DATA)
    assertRedirects(response, f'{url}{COMMENTS_REDIRECT}')
    comments_after = Comment.objects.count()
    assert (comments_after - comments_before) == COMMENT_ADD_TRUE
    comment = Comment.objects.last()
    assert comment.text == COMMENT_TEXT
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, news):
    """Проверка обсценной лексики."""
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    url = reverse('news:detail', args=(news.id,))
    comments_before = Comment.objects.count()
    response = author_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_after = Comment.objects.count()
    assert (comments_after - comments_before) == COMMENT_ADD_DELETE_FALSE


def test_author_can_delete_comment(author_client, comment, news):
    """Авторизованный пользователь может удалять свои комментарии."""
    news_url = reverse('news:detail', args=(news.id,))
    delete_url = reverse('news:delete', args=(comment.id,))
    url_to_comments = news_url + f'{COMMENTS_REDIRECT}'
    comments_before = Comment.objects.count()
    response = author_client.delete(delete_url)
    assertRedirects(response, url_to_comments)
    with pytest.raises(Comment.DoesNotExist):
        Comment.objects.get(pk=comment.id)
    comments_after = Comment.objects.count()
    assert (comments_after - comments_before) == COMMENT_DELETE_TRUE


def test_user_cant_delete_comment_of_another_user(not_author_client, comment):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    delete_url = reverse('news:delete', args=(comment.id,))
    comments_before = Comment.objects.count()
    response = not_author_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_after = Comment.objects.count()
    assert (comments_after - comments_before) == COMMENT_ADD_DELETE_FALSE


def test_author_can_edit_comment(author, author_client, comment, news):
    """Авторизованный пользователь может редактировать свои комментарии."""
    news_url = reverse('news:detail', args=(news.id,))
    url_to_comments = news_url + '#comments'
    edit_url = reverse('news:edit', args=(comment.id,))
    comments_before = Comment.objects.count()
    response = author_client.post(edit_url, data=NEW_FORM_DATA)
    assertRedirects(response, url_to_comments)
    comments_after = Comment.objects.count()
    assert (comments_after - comments_before) == COMMENT_EDIT_TRUE
    comment.refresh_from_db()
    assert comment.text == NEW_COMMENT_TEXT
    assert comment.news == news
    assert comment.author == author


def test_user_cant_edit_comment_of_another_user(author, not_author_client,
                                                comment, news):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    edit_url = reverse('news:edit', args=(comment.id,))
    response = not_author_client.post(edit_url, data=NEW_FORM_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == COMMENT_TEXT
    assert comment.news == news
    assert comment.author == author
