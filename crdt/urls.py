from django.conf.urls import url, include
from django.contrib import admin

from . import views
from . import api

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),

    url(r'^$', views.index, name='index'),
    url(r'^login$', views.login_view, name='login'),
    url(r'^logout$', views.logout_view, name='logout'),
    url(r'^register$', views.register, name='register'),
    url(r'^set_pagination/(?P<active_folder_id>inbox|outbox)/(?P<mark>readed|unreaded)/$', views.set_pagination, name='set_pagination'),
    url(r'^set_pagination/(?P<active_folder_id>[-\w]+)/(?P<mark>readed|unreaded)/$', views.set_pagination, name='set_pagination'),
    url(r'^mark/(?P<message_id>[-\w]+)/(?P<active_folder_id>inbox|outbox)/(?P<mark>readed|unreaded)/$', views.mark, name='mark'),
    url(r'^mark/(?P<message_id>[-\w]+)/(?P<active_folder_id>[-\w]+)/(?P<mark>readed|unreaded)/$', views.mark, name='mark'),
    url(r'^show_messages/(?P<active_folder_id>inbox|outbox)/(?P<mark>readed|unreaded)/(?P<msg_slice>.+)/$', views.show_messages, name='show_messages'),
    url(r'^show_messages/(?P<active_folder_id>[-\w]+)/(?P<mark>readed|unreaded)/(?P<msg_slice>.+)/$', views.show_messages, name='show_messages'),
    url(r'^delete/(?P<active_folder_id>[-\w]+)/(?P<message_id>[-\w]+)/(?P<mark>readed|unreaded)/$', views.delete, name='delete'),
    url(r'^delete_folder/(?P<active_folder_id>[-\w]+)/$', views.delete_folder, name='delete_folder'),
    url(r'^change_folder/(?P<active_folder_id>[-\w]+)/(?P<message_id>[-\w]+)/(?P<mark>readed|unreaded)/$', views.change_folder, name='change_folder'),
    url(r'^add_folder/(?P<active_folder_id>[-\w]+)/(?P<mark>readed|unreaded)/$', views.add_folder, name='add_folder'),
    url(r'^send_message/(?P<active_folder_id>[-\w]+)/(?P<mark>readed|unreaded)/$', views.send_message, name='send_message'),
    url(r'^send_message/(?P<active_folder_id>inbox|outbox)/(?P<mark>readed|unreaded)/$', views.send_message, name='send_message'),
    url(r'^receive/', views.receive, name='receive'),

    url(r'^api_register$', api.api_register),
    url(r'^api_login$', api.api_login),
    url(r'^api_logout$', api.api_logout),
    url(r'^api_addMessage$', api.api_addMessage),
    url(r'^api_deleteMessage$', api.api_deleteMessage),
    url(r'^api_addFolder$', api.api_addFolder),
    url(r'^api_deleteFolder$', api.api_deleteFolder),
    url(r'^api_mark_readed$', api.api_mark_readed),
    url(r'^api_mark_unreaded$', api.api_mark_unreaded),
    url(r'^api_getState$', api.api_getState),
    url(r'^api_getWait$', api.api_getWait),
    url(r'^api_changeFolder$', api.api_changeFolder),
    url(r'^api_getOutbox$', api.api_getOutbox),
    url(r'^api_getInbox$', api.api_getInbox),
    url(r'^api_getFolders$', api.api_getFolders),
    url(r'^api_getInFolder$', api.api_getInFolder),
    url(r'^api_getAllMessages$', api.api_getAllMessages),
    url(r'^api_getReadedMessages$', api.api_getReadedMessages),
    url(r'^api_getUnreadedMessages$', api.api_getUnreadedMessages),
]