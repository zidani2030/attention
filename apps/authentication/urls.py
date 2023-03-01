# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, include
from .views import login_view, register_user
from django.contrib.auth.views import LogoutView

from ..home.views import update_user_subscriptions, send_email, get_subscription, subscription_list, \
    subscription_create, subscription_detail, subscription_edit, subscription_delete

urlpatterns = [
    path('login/', login_view, name="login"),
    path('register/', register_user, name="register"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path('social_login/', include('allauth.urls')),
    path('update_user_subscription/<id>/', update_user_subscriptions, name='update_user_subscriptions'),
    path('send-email/', send_email, name='send_email'),
    path('list_sub/', subscription_list, name='subscription_list'),
    path('create/', subscription_create, name='subscription_create'),
    path('<pk>/', subscription_detail, name='subscription_detail'),
    path('<pk>/edit/', subscription_edit, name='subscription_edit'),
    path('<pk>/delete/', subscription_delete, name='subscription_delete'),
    path('subscription/<id>/', get_subscription, name='subscription'),
]
