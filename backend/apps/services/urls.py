from django.urls import path
from .views import GarageListView, CreateAppointmentView, AppointmentHistoryView, MechanicAppointmentListView, UpdateAppointmentStatusView, ConfirmAppointmentPaymentView, VerifyAppointmentPaymentView, MechanicServiceListCreateView, MechanicServiceDetailView
from .revenue_view import MechanicRevenueView
from .review_view import CreateReviewView

urlpatterns = [
    path('garages/', GarageListView.as_view(), name='garage-list'),
    path('book/', CreateAppointmentView.as_view(), name='book-appointment'),
    path('history/', AppointmentHistoryView.as_view(), name='appointment-history'),
    path('mechanic/list/', MechanicAppointmentListView.as_view(), name='mechanic-appt-list'),
    path('mechanic/services/', MechanicServiceListCreateView.as_view(), name='mechanic-services-list'),
    path('mechanic/services/<int:pk>/', MechanicServiceDetailView.as_view(), name='mechanic-services-detail'),
    path('<int:pk>/update-status/', UpdateAppointmentStatusView.as_view(), name='update-appt-status'),
    path('<int:pk>/confirm-payment/', ConfirmAppointmentPaymentView.as_view(), name='confirm-appt-payment'),
    path('<int:pk>/verify-payment/', VerifyAppointmentPaymentView.as_view(), name='verify-appt-payment'),
    path('mechanic/revenue/', MechanicRevenueView.as_view(), name='mechanic-revenue'),
    path('review/add/', CreateReviewView.as_view(), name='add-review'),
]
