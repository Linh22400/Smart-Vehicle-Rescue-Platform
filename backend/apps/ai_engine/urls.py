from django.urls import path
from .views import AnalyzeDamageView

urlpatterns = [
    path('analyze-damage/', AnalyzeDamageView.as_view(), name='analyze-damage'),
]
