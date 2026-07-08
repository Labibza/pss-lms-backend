from django.contrib.auth.views import LoginView
from django.urls import path

from . import views

urlpatterns = [
    # Halaman umum
    path("", views.home, name="home"),
    path("users/", views.user_list, name="user_list"),
    path("courses/", views.course_list, name="course_list"),
    path("courses/<int:course_id>/", views.course_detail, name="course_detail"),

    # Auth
    path(
        "login/",
        LoginView.as_view(
            template_name="core/login.html",
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path("logout/", views.logout_post, name="logout"),

    # Course user
    path("courses/<int:course_id>/join/", views.join_course, name="join_course"),
    path("my-courses/", views.my_courses, name="my_courses"),
    path("dashboard/", views.dashboard, name="dashboard"),

    # Content dan comment
    path(
        "contents/<int:content_id>/",
        views.course_content_detail,
        name="course_content_detail",
    ),
    path(
        "contents/<int:content_id>/comment/",
        views.add_comment,
        name="add_comment",
    ),
    path(
        "contents/<int:content_id>/edit/",
        views.edit_content,
        name="edit_content",
    ),

    # Statistik
    path("statistics/courses/", views.course_stat, name="course_stat"),
    path("statistics/users/", views.user_statistics, name="user_statistics"),

    # Import CSV
    path("import-csv/", views.upload_csv, name="upload_csv"),

    # API sederhana
    path("api/courses/", views.api_courses, name="api_courses"),
    path("api/courses/<int:course_id>/", views.api_course_detail, name="api_course_detail"),
]