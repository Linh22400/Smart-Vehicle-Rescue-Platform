from django.urls import path
from .views import AnalyzeDamageView, AIReportListView, AIReportDeleteView, AIReportCleanupView
from .analyze_sound import AnalyzeSoundView

urlpatterns = [
    path('analyze-damage/', AnalyzeDamageView.as_view(), name='analyze-damage'),
    path('analyze-sound/',  AnalyzeSoundView.as_view(),  name='analyze-sound'),
    path('history/', AIReportListView.as_view(), name='ai-history'),
    path('history/<int:pk>/delete/', AIReportDeleteView.as_view(), name='ai-report-delete'),
    path('history/cleanup/', AIReportCleanupView.as_view(), name='ai-report-cleanup'),
]
