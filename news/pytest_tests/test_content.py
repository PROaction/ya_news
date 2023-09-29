import pytest

from conftest import HOME_URL
from django.conf import settings

from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count(two_page_from_newses, client):
    response = client.get(HOME_URL)
    newses = response.context['object_list']
    news_count = len(newses)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(two_page_from_newses, client):
    response = client.get(HOME_URL)
    newses = response.context['object_list']
    all_dates = [news.date for news in newses]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, news, two_comments_from_news, detail_url):
    response = client.get(detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    expected_result = news.comment_set.all()
    assert list(all_comments) == list(expected_result)


@pytest.mark.parametrize(
    ('user_client', 'form_in_context'), (
        (pytest.lazy_fixture('client'), False),
        (pytest.lazy_fixture('admin_client'), True)
    )
)
@pytest.mark.django_db
def test_anon_and_authorized_clients_has_form(
    client, news, detail_url, user_client, form_in_context
):
    response = user_client.get(detail_url)
    assert ('form' in response.context) is form_in_context


@pytest.mark.django_db
def test_instance_form(admin_client, news, detail_url):
    response = admin_client.get(detail_url)
    form = response.context.get('form')
    assert isinstance(form, CommentForm)
