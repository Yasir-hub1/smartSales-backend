from django.urls import path
from . import views

urlpatterns = [
    # Métodos de pago
    path('methods/', views.PaymentMethodListView.as_view(), name='payment_methods'),
    path('methods/available/', views.get_payment_methods, name='available_payment_methods'),
    
    # Pagos
    path('payments/', views.PaymentListCreateView.as_view(), name='payment_list_create'),
    path('payments/<uuid:pk>/', views.PaymentDetailView.as_view(), name='payment_detail'),
    path('payments/<uuid:payment_id>/status/', views.get_payment_status, name='payment_status'),
    path('payments/<uuid:payment_id>/refund/', views.create_refund, name='create_refund'),
    
    # Stripe
    path('stripe/create-intent/', views.create_payment_intent, name='create_payment_intent'),
    path('stripe/confirm/', views.confirm_payment, name='confirm_payment'),
    path('stripe/webhook/', views.stripe_webhook, name='stripe_webhook'),
    
    # Pagos de ventas
    path('sales/<uuid:sale_id>/process/', views.process_sale_payment, name='process_sale_payment'),
]