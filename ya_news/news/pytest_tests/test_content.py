import pytest
from django.conf import settings
from django.urls import reverse
from news.forms import CommentForm


URL_HOME: str = reverse('news:home')
CONTEXT_OBJECT_HOME: str = 'object_list'
CONTEXT_OBJECT_DETAIL: str = 'news'
CONTEXT_OBJECT_FORM: str = 'form'


@pytest.mark.django_db
def test_news_count(client, all_news):
    """Количество новостей на главной странице — не более 10."""
    url = URL_HOME
    response = client.get(url)
    object_list = response.context[CONTEXT_OBJECT_HOME]
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, all_news):
    """Новости отсортированы от самой свежей к самой старой."""
    url = URL_HOME
    response = client.get(url)
    object_list = response.context[CONTEXT_OBJECT_HOME]
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, news):
    """Комментарии на странице отдельной новости отсортированы."""
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert CONTEXT_OBJECT_DETAIL in response.context
    news = response.context[CONTEXT_OBJECT_DETAIL]
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, news):
    """Анонимному пользователю недоступна форма для отправки комментария."""
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert CONTEXT_OBJECT_FORM not in response.context


@pytest.mark.django_db
def test_authorized_client_has_form(author_client, news):
    """Авторизованному пользователю доступна форма для отправки комментария."""
    url = reverse('news:detail', args=(news.id,))
    response = author_client.get(url)
    assert CONTEXT_OBJECT_FORM in response.context
    assert isinstance(response.context[CONTEXT_OBJECT_FORM], CommentForm)
