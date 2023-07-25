from django.urls import path
from . import views


urlpatterns = [
    path('', views.index),
    path('register-accounts', views.register_accounts),
    path('get-money', views.get_money),
    path('send-review', views.send_reviews),
    path('review-pattern', views.review_pattern),
    path('review/<int:article>/', views.send_review),
    path('ransoms', views.get_ransoms),
    path('get-codes', views.get_codes)
]
