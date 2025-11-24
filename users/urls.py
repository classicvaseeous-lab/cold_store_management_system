# users/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "users"

urlpatterns = [
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="users/login.html"),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="users:login"),
        name="logout",
    ),
    path("dashboard/", views.dashboard_view, name="dashboard"),
]





# from django.urls import path
# from django.contrib.auth import views as auth_views
# from . import views
# app_name = 'users'  #  namespace for the users app


# urlpatterns = [
#     path("login/", auth_views.LoginView.as_view(template_name="users/login.html"), name="login"),
#     path("logout/", auth_views.LogoutView.as_view(next_page="users:login"), name="logout"),
#     path("dashboard/", views.dashboard, name="dashboard"),
# ]

# urlpatterns = [
#     path("login/", auth_views.LoginView.as_view(template_name="users/login.html"), name="login"),
#     path("logout/", auth_views.LogoutView.as_view(), name="logout"),
#     path("dashboard/", views.dashboard, name="dashboard"),
# ]
# urlpatterns = [
#     path('login/', views.CustomLoginView.as_view(), name='login'),
#     path('logout/', views.logout_view, name='logout'),
#     path('dashboard/', views.dashboard_view, name='dashboard'),
# ]