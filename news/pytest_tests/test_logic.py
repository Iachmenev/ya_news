import pytest

from http import HTTPStatus
from pytest_django.asserts import assertRedirects
from django.test.client import Client

from django.urls import reverse

from news.forms import WARNING,BAD_WORDS
from news.models import News, Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(news, form_data):
    detail_url = reverse('news:detail', args=(news.id,))
    Client().post(detail_url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_can_create_comment(form_data, author_client, news, author):
    detail_url = reverse('news:detail', args=(news.id,))
    response = author_client.post(detail_url, data=form_data)
    assertRedirects(response, f'{detail_url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.first()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author

@pytest.mark.django_db
def test_user_cant_use_bad_words(author_client, news):
    detail_url = reverse('news:detail', args=(news.id,))
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(detail_url, data=bad_words_data)
    assert response.context['form'].errors['text'] == [WARNING]
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(author_client, comment):
    delete_url = reverse('news:delete', args=(comment.id,))
    response = author_client.delete(delete_url)
    assert response.url == reverse('news:detail',
                                   args=(comment.news.id,)) + '#comments'
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_cant_delete_comment_of_another_user(not_author_client, comment):
    delete_url = reverse('news:delete', args=(comment.id,))
    response = not_author_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_author_can_edit_comment(author_client, comment, form_data):
    edit_url = reverse('news:edit', args=(comment.id,))
    response = author_client.post(edit_url, data=form_data)
    assertRedirects(response, reverse('news:detail',
                                      args=(comment.news.id,)) + '#comments')
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_user_cant_edit_comment_of_another_user(
        not_author_client,
        comment,
        form_data
):
    edit_url = reverse('news:edit', args=(comment.id,))
    response = not_author_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text != form_data['text']
