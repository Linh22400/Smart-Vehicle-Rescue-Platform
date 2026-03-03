from django.urls import path
from .views import AnalyzeDamageView, AIReportListView, AIReportDeleteView, AIReportCleanupView

urlpatterns = [
    path('analyze-damage/', AnalyzeDamageView.as_view(), name='analyze-damage'),
    path('history/', AIReportListView.as_view(), name='ai-history'),
    path('history/<int:pk>/delete/', AIReportDeleteView.as_view(), name='ai-report-delete'),
    path('history/cleanup/', AIReportCleanupView.as_view(), name='ai-report-cleanup'),
]
