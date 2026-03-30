from django.urls import path
from . import personal_views

urlpatterns = [
    # Personal Dashboard
    path('dashboard/', personal_views.personal_dashboard, name='personal_dashboard'),
    
    # Expense Tracker
    path('expenses/', personal_views.expense_tracker, name='expense_tracker'),
    path('expenses/add/', personal_views.add_expense, name='add_expense'),
    path('expenses/export/', personal_views.export_expenses, name='export_expenses'),
    path('expenses/analytics/', personal_views.expense_analytics_api, name='expense_analytics_api'),
    
    # Travel Budget
    path('budget/', personal_views.travel_budget, name='travel_budget'),
    path('budget/add/', personal_views.add_budget, name='add_budget'),
    path('budget/update/<int:budget_id>/', personal_views.update_budget, name='update_budget'),
    
    # Travel Wishlist
    path('wishlist/', personal_views.travel_wishlist, name='travel_wishlist'),
    path('wishlist/add/', personal_views.add_wishlist_item, name='add_wishlist_item'),
    path('wishlist/toggle/<int:item_id>/', personal_views.toggle_wishlist_status, name='toggle_wishlist_status'),
    
    # Travel Documents
    path('documents/', personal_views.travel_documents, name='travel_documents'),
    path('documents/add/', personal_views.add_document, name='add_document'),
    
    # User Preferences
    path('preferences/', personal_views.user_preferences, name='user_preferences'),
]