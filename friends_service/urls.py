import os

from django.urls import path
from rest_framework import permissions
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from friends import views

basedir = os.path.abspath(os.path.dirname(__file__))
schema_view = get_schema_view(
    openapi.Info(
        title="Friends Service API",
        default_version='v1',
        contact=openapi.Contact(name="Batyrev Vladislav",
                                email="batyrev-vr@yandex.ru")
    ),
    public=True,
    permission_classes=(permissions.AllowAny,)
)

urlpatterns = [
    path('', views.api_root),
    path('users/', views.UserListCreateView.as_view(),
         name='user-list-create'),
    path('users/<int:pk>/', views.UserDetailView.as_view(),
         name='user-detail'),
    path('users/<int:pk>/friends/', views.FriendsListView.as_view(),
         name='friends-list'),
    path('users/<int:pk>/friendship/status/<int:friend_id>/', views.UserFriendshipStatusView.as_view(),
         name='friendship-status'),
    path('users/<int:from_user_id>/friendship/update/<int:friend_id>/', views.UserFriendshipUpdateView.as_view(),
         name='friendship-update'),
    path('friendship/create/', views.FriendshipCreateView.as_view(),
         name='friendship-create'),
    path('friendship/update/<int:pk>/', views.FriendshipUpdateView.as_view(),
         name='friendship-update'),
    path('friendship/status/<int:pk>/', views.FriendshipStatusView.as_view(),
         name='friendship-status'),
    path('friendship/delete/<int:pk>/', views.FriendshipDeleteView.as_view(),
         name='friendship-delete'),
    path('friendship/outgoing/<int:user_id>/', views.OutgoingFriendshipRequestsView.as_view(),
         name='outgoing-friendship-requests'),
    path('friendship/incoming/<int:user_id>/', views.IncomingFriendshipRequestsView.as_view(),
         name='incoming-friendship-requests'),
    path('friendship/accepted/<int:user_id>/', views.AcceptedFriendshipRequestsView.as_view(),
         name='accepted-friendship-requests'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0),
         name='schema-redoc'),
    path('swagger.yaml', schema_view.without_ui(cache_timeout=0),
         name='schema-yaml'),
]
