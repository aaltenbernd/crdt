from django.conf.urls import url, include
from django.contrib import admin

from .templates import template_views
from . import receive
from . import api

urlpatterns = [
    # Template URLs

    url(r'^admin/', include(admin.site.urls)),

    url(r'^$', template_views.index, name='index'),
    url(r'^login$', template_views.login_view, name='login'),
    url(r'^logout$', template_views.logout_view, name='logout'),
    url(r'^register$', template_views.register, name='register'),
    url(
        r'^set_pagination/(?P<active_folder_id>inbox|outbox)/(?P<mark>read|unread)/$', 
        template_views.set_pagination, 
        name='set_pagination'
    ),
    url(
        r'^set_pagination/(?P<active_folder_id>[-\w]+)/(?P<mark>read|unread)/$', 
        template_views.set_pagination, name='set_pagination'
    ),
    url(
        r'^mark/(?P<message_id>[-\w]+)/(?P<active_folder_id>inbox|outbox)/(?P<mark>read|unread)/$', 
        template_views.mark, 
        name='mark'
    ),
    url(
        r'^mark/(?P<message_id>[-\w]+)/(?P<active_folder_id>[-\w]+)/(?P<mark>read|unread)/$', 
        template_views.mark, 
        name='mark'
    ),
    url(
        r'^show_messages/(?P<active_folder_id>inbox|outbox)/(?P<mark>read|unread)/(?P<msg_slice>.+)/$', 
        template_views.show_messages, 
        name='show_messages'
    ),
    url(
        r'^show_messages/(?P<active_folder_id>[-\w]+)/(?P<mark>read|unread)/(?P<msg_slice>.+)/$', 
        template_views.show_messages, 
        name='show_messages'
    ),
    url(
        r'^delete/(?P<active_folder_id>[-\w]+)/(?P<message_id>[-\w]+)/(?P<mark>read|unread)/$', 
        template_views.delete, 
        name='delete'
    ),
    url(
        r'^delete_folder/(?P<active_folder_id>[-\w]+)/$', 
        template_views.delete_folder, 
        name='delete_folder'
    ),
    url(
        r'^change_folder/(?P<active_folder_id>[-\w]+)/(?P<message_id>[-\w]+)/(?P<mark>read|unread)/$', 
        template_views.change_folder, 
        name='change_folder'
    ),
    url(
        r'^add_folder/(?P<active_folder_id>[-\w]+)/(?P<mark>read|unread)/$', 
        template_views.add_folder, 
        name='add_folder'
    ),
    url(
        r'^send_message/(?P<active_folder_id>[-\w]+)/(?P<mark>read|unread)/$', 
        template_views.send_message, 
        name='send_message'
    ),
    url(
        r'^send_message/(?P<active_folder_id>inbox|outbox)/(?P<mark>read|unread)/$', 
        template_views.send_message, 
        name='send_message'
    ),

    # URL for receiving operations from other hosts
    
    url(r'^receive/', receive.receive, name='receive'),

    # API URLs

    url(r'^api_register$', api.api_register),
    url(r'^api_login$', api.api_login),
    url(r'^api_logout$', api.api_logout),
    url(r'^api_addMessage$', api.api_addMessage),
    url(r'^api_deleteMessage$', api.api_deleteMessage),
    url(r'^api_addFolder$', api.api_addFolder),
    url(r'^api_deleteFolder$', api.api_deleteFolder),
    url(r'^api_markRead$', api.api_markRead),
    url(r'^api_markUnread$', api.api_markUnread),
    url(r'^api_getState$', api.api_getState),
    url(r'^api_getWait$', api.api_getWait),
    url(r'^api_changeFolder$', api.api_changeFolder),
    url(r'^api_getOutbox$', api.api_getOutbox),
    url(r'^api_getInbox$', api.api_getInbox),
    url(r'^api_getFolders$', api.api_getFolders),
    url(r'^api_getInFolder$', api.api_getInFolder),
    url(r'^api_getAllMessages$', api.api_getAllMessages),
    url(r'^api_getReadMessages$', api.api_getReadMessages),
    url(r'^api_getUnreadMessages$', api.api_getUnreadMessages),
]