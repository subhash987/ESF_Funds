from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

# app_name = 'loan'

urlpatterns = [
    path('login/', views.loginUser, name="loginpage"),
    # path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='loginpage'),
    path('logout/', views.logoutUser, name="logoutpage"),
    path('register/', views.registerUser, name="registerpage"),

    path('', views.home, name='home'),

    path('profile/', views.profiles, name="profile"),
    path('admin-profile/', views.admin_profile, name="admin-profile"),
    path('create-profile/', views.createProfile, name="create-profile"),
    path('update-profile/<str:pk>', views.updateProfile, name="update-profile"),
    path('delete-profile/<str:pk>/', views.deleteProfile, name="delete-profile"),
    
    path('loans/', views.loans, name="loans"),
    path('loan-details/<int:pk>', views.loan_details, name="loan-details"),
    path('create-loan/', views.create_loan, name="create-loan"),
    path('update-loan/<int:pk>', views.updateLoan, name="update-loan"),
    path('delete-loan/<str:pk>', views.deleteLoan, name="delete-loan"),
    path('loan_success/<int:pk>', views.loan_success, name="loan_success"),
    
    path('transactions/', views.transactions, name="transactions"),
    path('create-transaction/', views.createTransaction, name="create-transaction"),
    path('update-transaction/<int:pk>/', views.updateTransaction, name="update-transaction"),
    path('delete-transaction/<str:pk>/', views.deleteTransaction, name="delete-transaction"),
    
    path('about/', views.about, name="about"),
    path('contact/', views.contact, name="contact"),
    path('repay-loan/<int:loan_id>/', views.repay_loan, name='repay_loan'),
    path('loan/<int:pk>/transactions/', views.view_loan_transactions, name='view-loan-transactions'),

    path('funds/', views.funds_page, name='funds_page'),
    
]
