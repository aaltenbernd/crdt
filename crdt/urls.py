from django.conf.urls import url
from . import views
from . import connect

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^delete_all', views.delete_all, name='delete_all')
    url(r'^increment$', views.increment, name='increment'),
    url(r'^decrement$', views.decrement, name='decrement'),
    url(r'^delete$', views.delete, name='delete'),
    url(r'^receive/', connect.receive, name='receive')
]