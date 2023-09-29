import random
from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from conftest import COMMENT_TEXT, NEW_COMMENT_TEXT
from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
    client, news, form_data, detail_url
):
    expected_comments_count = news.comment_set.count()
    client.post(detail_url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == expected_comments_count


def test_user_can_create_comment(
    admin_user, admin_client, news, form_data, detail_url
):
    comments_count = Comment.objects.count()

    response = admin_client.post(detail_url, data=form_data)
    assertRedirects(response, f'{detail_url}#comments')

    actual_comments_count = Comment.objects.count()
    assert actual_comments_count == comments_count + 1
    comment = Comment.objects.get()
    assert comment.text == NEW_COMMENT_TEXT
    assert comment.news == news
    assert comment.author == admin_user


def test_user_cant_use_bad_words(admin_client, news, detail_url):
    expected_comments_count = news.comment_set.count()

    bad_words_data = {'text': (f'Какой-то текст, '
                               f'{random.choice(BAD_WORDS)}, еще текст')}
    response = admin_client.post(detail_url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == expected_comments_count


def test_author_can_delete_comment(
    author_client, news, comment, detail_url, delete_comment_url
):
    url_to_comments = detail_url + '#comments'
    expected_comments_count = news.comment_set.count() - 1

    response = author_client.delete(delete_comment_url)
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == expected_comments_count


def test_author_can_edit_comment(
    author_client, form_data, news, comment, edit_comment_url, detail_url
):
    url_to_comments = detail_url + '#comments'
    expected_author = comment.author
    expected_news = comment.news

    response = author_client.post(edit_comment_url, data=form_data)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == NEW_COMMENT_TEXT
    assert comment.author == expected_author
    assert comment.news == expected_news


def test_user_cant_edit_comment_of_another_user(
        reader_client, form_data, news, comment, edit_comment_url
):
    expected_author = comment.author
    expected_news = comment.news

    response = reader_client.post(edit_comment_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == COMMENT_TEXT
    assert comment.author == expected_author
    assert comment.news == expected_news
