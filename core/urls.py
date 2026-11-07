from django.urls import path
from .api_views import BlackboardSyncAPIView
from .views import dashboard_view, course_detail_view

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    path('course/<int:course_id>/', course_detail_view, name='course_detail'),
    path('api/sync/', BlackboardSyncAPIView.as_view(), name='blackboard-sync'),
]