from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("view-loan/<int:loan_id>/", views.view_loan_by_loan_id, name="view_loan_by_loan_id"),
    path("view-loans/<int:customer_id>", views.view_loans_by_customer_id, name="view_loans_by_customer_id"),
]