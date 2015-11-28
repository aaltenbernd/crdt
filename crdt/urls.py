from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^increment$', views.increment, name='increment'),
    url(r'^decrement$', views.decrement, name='decrement'),
    url(r'^delete$', views.delete, name='delete')
]