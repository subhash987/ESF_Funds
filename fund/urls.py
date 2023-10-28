from django.urls import path
from . import views

app_name = 'fund'

urlpatterns = [
    path('contributor-details/', views.contributor_list, name='contributor_list'),
    path('make-contribution/<int:contributor_id>/', views.make_contribution, name='make_contribution'),
    path('contribution-history/<int:contributor_id>/', views.contribution_history, name='contribution_history'),
    path('create-contributor/', views.create_contributor, name='create_contributor'),
    path('edit-contribution/<int:contribution_id>/', views.edit_contribution, name='edit_contribution'),
    path('delete-contributor/<int:contributor_id>/', views.delete_contributor, name='delete_contributor'),
    path('contributor-transactions/', views.contributor_transactions, name='contributor_transactions'),
    # path('give-bonus/', views.give_bonus, name='give_bonus'),
    # path('bonus-transactions/', views.bonus_transactions, name='bonus_transactions'),
]