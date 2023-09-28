from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    ('name', 'args'),
    (
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('pk_for_args')),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
    )
)
@pytest.mark.django_db
def test_pages_availability(name, args, client):
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code, HTTPStatus.OK


@pytest.mark.parametrize(
    ('user_client', 'expected_status'),
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('reader_client'), HTTPStatus.NOT_FOUND),
    )
)
@pytest.mark.parametrize(
    ('template_name', 'args'),
    (
        ('news:edit', pytest.lazy_fixture('pk_for_args')),
        ('news:delete', pytest.lazy_fixture('pk_for_args'))
    )
)
def test_availability_for_comment_edit_and_delete(
        user_client, expected_status, template_name, args, news, comment
):
    url = reverse(template_name, args=args)
    response = user_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    ('template_name', 'args'),
    (
        ('news:edit', pytest.lazy_fixture('pk_for_args')),
        ('news:delete', pytest.lazy_fixture('pk_for_args'))
    )
)
@pytest.mark.django_db
def test_redirect_for_anonymous_client(
        client, template_name, args
):
    login_url = reverse('users:login')
    url = reverse(template_name, args=args)
    redirect_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, redirect_url)
