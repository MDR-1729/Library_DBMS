from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("books/", views.book_list, name="book_list"),
    path("books/add/", views.book_create, name="book_create"),
    path("books/<int:pk>/edit/", views.book_update, name="book_update"),
    path("books/<int:pk>/delete/", views.book_delete, name="book_delete"),
    path("members/", views.member_list, name="member_list"),
    path("members/add/", views.member_create, name="member_create"),
    path("members/<int:pk>/edit/", views.member_update, name="member_update"),
    path("members/<int:pk>/delete/", views.member_delete, name="member_delete"),
    path("loans/", views.loan_list, name="loan_list"),
    path("loans/issue/", views.loan_create, name="loan_create"),
    path("loans/<int:pk>/return/", views.loan_return, name="loan_return"),
]
