"""tjbash URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from quotes import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.index_view, name="index"),
    url(r'^quotes/all/$', views.view_all_quotes, name="all_quotes"),
    url(r'^quotes/unapproved/$', views.view_unapproved_quotes, name="unapproved_quotes"),
    url(r'^quotes/top/$', views.view_top_quotes, name="top_quotes"),
    url(r'^quotes/bottom/$', views.view_bottom_quotes, name="bottom_quotes"),
    url(r'^quotes/new/$', views.create_new_quote, name="new_quote"),
    url(r'^tags/$', views.view_all_tags, name="view_all_tags"),
    url(r'^quotes/tag/$', views.view_quotes_by_tag, name="quotes_by_tag"),
    url(r'^quotes/approve/(?P<qid>\d+)/$', views.approve_quote, name="approve_quote"),
    url(r'^quotes/delete/$', views.delete_quote, name="delete_quote"),
    url(r'^quotes/edit/(?P<qid>\d+)/', views.edit_quote, name="edit_quote"),
    url(r'^quotes/upvote/', views.upvote_quote, name="upvote_quote"),
    url(r'^quotes/downvote/', views.downvote_quote, name="downvote_quote"),
    url(r'^quotes/permalink/(?P<qid>\d+)/$', views.view_quote, name="view_quote"),
    url(r'^announcements/new/$', views.add_announcement, name="new_announcement"),
    url(r'^announcements/edit/(?P<aid>\d+)/', views.edit_announcement, name="edit_announcement"),
]
