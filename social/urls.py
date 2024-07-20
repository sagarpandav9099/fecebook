from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings



urlpatterns = [
    path('', views.home, name='home'),

    # promotion urls
    path('like/<int:post_id>/', views.like_post, name='like-post'),
    path('post/<int:post_id>/comment/', views.post_comment, name='post-comment'),

    # profile url
    path('profile_management', views.profile_management, name='profile-management'),

    # friend urls
    path('friend/', views.friend_view, name='friend-view'),
    path('send_friend_request/<int:user_id>/', views.send_friend_request, name='send-friend-request'),
    path('accept_friend_request/<int:request_id>/', views.accept_friend_request, name='accept-friend-request'),

    # group urls
    path('group_list/', views.group_list, name='group_list'),
    path('group_create/', views.create_group, name='create_group'),
    path('group_join/<int:group_id>/', views.join_group, name='join_group'),
    path('group_leave/<int:group_id>/', views.leave_group, name='leave_group'),
    path('group_chat/<int:group_id>/', views.group_chat, name='group_chat'),
    path('groups_detail/<int:group_id>/', views.group_detail, name='group_detail'),

    # notification urls
    path('notification/', views.notification_list, name='notification_list'),
    path('notification_read/<int:notification_id>/', views.mark_as_read, name='mark_as_read'),
    path('fetch-notifications/', views.fetch_notifications, name='fetch_notifications'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)