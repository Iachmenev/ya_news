import pytest

from django.urls import reverse
from news.forms import CommentForm
from django.conf import settings

HOME_URL = reverse('news:home')


@pytest.mark.django_db
def test_news_count(client, all_news):
    response = client.get(HOME_URL)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, all_news):
    response = client.get(HOME_URL)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(all_comments, client, news):
    detail_url = reverse('news:detail', args=(news.id,))
    response = client.get(detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, news):
    detail_url = reverse('news:detail', args=(news.id,))
    response = client.get(detail_url)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_client_has_form(author_client, news):
    detail_url = reverse('news:detail', args=(news.id,))
    response = author_client.get(detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
