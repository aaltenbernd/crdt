from django.conf.urls import url
from . import views
from . import api

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login$', views.login_view, name='login'),
    url(r'^logout$', views.logout_view, name='logout'),
    url(r'^register$', views.register, name='register'),
    url(r'^delete_all$', views.delete_all, name='delete_all'),
    url(r'^show_messages/(?P<active_folder_id>[-\w]+)/$', views.show_messages, name='show_messages'),
    url(r'^delete/(?P<active_folder_id>[-\w]+)/(?P<message_id>[-\w]+)/$', views.delete, name='delete'),
    url(r'^delete_folder/(?P<active_folder_id>[-\w]+)/$', views.delete_folder, name='delete_folder'),
    url(r'^change_folder/(?P<active_folder_id>[-\w]+)/(?P<message_id>[-\w]+)/$', views.change_folder, name='change_folder'),
    url(r'^add_folder/(?P<active_folder_id>[-\w]+)/$', views.add_folder, name='add_folder'),
    url(r'^send_message$', views.send_message, name='send_message'),
    url(r'^receive/', views.receive, name='receive'),

    url(r'^api_login$', api.api_login),
    url(r'^api_addMessage', api.api_addMessage),
    url(r'^api_deleteMessage/(?P<message_id>[-\w]+)/$', api.api_deleteMessage),
    url(r'^api_getCurrentState$', api.api_getCurrentState),
    url(r'^api_getQueue$', api.api_getQueue)
]