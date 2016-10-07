import django
from django.conf.urls import url
from .views import article_list,create_page,article_detail

import views

urlpatterns = [
    url(r'^list/(?P<block_id>\d+)', article_list),
    url(r'^createpage/(?P<block_id>\d+)',create_page),
    url(r'^detail/(?P<article_id>\d+)',article_detail),
]
