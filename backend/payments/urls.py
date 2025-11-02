from django.urls import path
from . import views

urlpatterns = [
    path('config/status/', views.ConfigStatusView.as_view(), name='config-status'),
    path('merchant-session/', views.MerchantSessionView.as_view(), name='merchant-session'),
    path('validate-merchant/', views.ValidateMerchantView.as_view(), name='validate-merchant'),
    path('onetime/session/', views.OneTimePaymentSessionView.as_view(), name='onetime-session'),
    path('onetime/process/', views.OneTimePaymentView.as_view(), name='onetime-process'),
    path('recurring/setup/', views.RecurringPaymentSetupView.as_view(), name='recurring-setup'),
    path('recurring/charge/', views.RecurringPaymentChargeView.as_view(), name='recurring-charge'),
]

