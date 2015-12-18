from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login$', views.login_view, name='login'),
    url(r'^logout$', views.logout_view, name='logout'),
    url(r'^delete_all$', views.delete_all, name='delete_all'),
    url(r'^show_messages$', views.show_messages, name='show_messages'),
    url(r'^delete$', views.delete, name='delete'),
    url(r'^receive/', views.receive, name='receive')
]