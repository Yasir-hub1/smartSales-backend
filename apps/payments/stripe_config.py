"""
Configuración de Stripe para SmartSales365
"""
import os
from django.conf import settings

# Configuración de Stripe
STRIPE_CONFIG = {
    'publishable_key': os.getenv('STRIPE_PUBLISHABLE_KEY', ''),
    'secret_key': os.getenv('STRIPE_SECRET_KEY', ''),
    'webhook_secret': os.getenv('STRIPE_WEBHOOK_SECRET', ''),
    'currency': 'MXN',
    'country': 'MX',
    'business_name': 'SmartSales365',
    'business_url': os.getenv('BUSINESS_URL', 'https://SmartSales365.com'),
}

# Métodos de pago por defecto
DEFAULT_PAYMENT_METHODS = [
    {
        'name': 'Tarjeta de Crédito/Débito',
        'code': 'stripe',
        'is_active': True,
        'is_online': True,
        'icon': '💳',
        'description': 'Pago con tarjeta de crédito o débito',
        'sort_order': 1
    },
    {
        'name': 'Efectivo',
        'code': 'cash',
        'is_active': True,
        'is_online': False,
        'icon': '💵',
        'description': 'Pago en efectivo',
        'sort_order': 2
    },
    {
        'name': 'Transferencia Bancaria',
        'code': 'transfer',
        'is_active': True,
        'is_online': False,
        'icon': '🏦',
        'description': 'Transferencia bancaria',
        'sort_order': 3
    }
]

# Configuración de webhooks
WEBHOOK_EVENTS = [
    'payment_intent.succeeded',
    'payment_intent.payment_failed',
    'payment_intent.canceled',
    'payment_intent.requires_action',
    'payment_method.attached',
    'customer.created',
    'customer.updated',
    'invoice.payment_succeeded',
    'invoice.payment_failed',
]

# Configuración de productos de Stripe
STRIPE_PRODUCT_CONFIG = {
    'name': 'SmartSales365 Product',
    'description': 'Producto vendido a través de SmartSales365',
    'type': 'service',
    'active': True,
}

# Configuración de precios
PRICE_CONFIG = {
    'currency': 'MXN',
    'recurring': None,  # Para pagos únicos
    'tax_behavior': 'inclusive',  # Los impuestos están incluidos
}

# Configuración de checkout
CHECKOUT_CONFIG = {
    'payment_method_types': ['card'],
    'mode': 'payment',
    'success_url': f"{STRIPE_CONFIG['business_url']}/tienda/payment/success",
    'cancel_url': f"{STRIPE_CONFIG['business_url']}/tienda/payment/cancel",
    'billing_address_collection': 'required',
    'shipping_address_collection': {
        'allowed_countries': ['MX'],
    },
    'customer_creation': 'always',
    'payment_intent_data': {
        'capture_method': 'automatic',
    },
}

# Configuración de elementos de Stripe
ELEMENTS_CONFIG = {
    'appearance': {
        'theme': 'stripe',
        'variables': {
            'colorPrimary': '#3498db',
            'colorBackground': '#ffffff',
            'colorText': '#2c3e50',
            'colorDanger': '#e74c3c',
            'fontFamily': 'Inter, system-ui, sans-serif',
            'spacingUnit': '4px',
            'borderRadius': '8px',
        },
        'rules': {
            '.Input': {
                'border': '1px solid #e0e0e0',
                'borderRadius': '8px',
                'padding': '12px',
            },
            '.Input:focus': {
                'border': '2px solid #3498db',
                'boxShadow': '0 0 0 3px rgba(52, 152, 219, 0.1)',
            },
            '.Label': {
                'fontWeight': '600',
                'color': '#2c3e50',
            },
            '.Error': {
                'color': '#e74c3c',
                'fontSize': '14px',
            },
        }
    },
    'locale': 'es',
}

# Configuración de notificaciones
NOTIFICATION_CONFIG = {
    'email_receipts': True,
    'email_receipts_from': os.getenv('STRIPE_EMAIL_FROM', 'noreply@SmartSales365.com'),
    'receipt_email_template': 'payment_receipt',
}

# Configuración de reembolsos
REFUND_CONFIG = {
    'automatic_refunds': False,
    'refund_reasons': [
        'duplicate',
        'fraudulent',
        'requested_by_customer',
    ],
    'refund_timeframe': 30,  # días
}

# Configuración de impuestos
TAX_CONFIG = {
    'tax_behavior': 'inclusive',
    'tax_code': 'txcd_99999999',  # Código de impuesto genérico
    'tax_rate': 0.16,  # 16% IVA
}

# Configuración de monedas soportadas
SUPPORTED_CURRENCIES = [
    'MXN',  # Peso mexicano
    'USD',  # Dólar estadounidense
]

# Configuración de países soportados
SUPPORTED_COUNTRIES = [
    'MX',  # México
    'US',  # Estados Unidos
]

# Configuración de límites
LIMITS_CONFIG = {
    'min_amount': 1.00,  # Mínimo 1 peso
    'max_amount': 1000000.00,  # Máximo 1 millón de pesos
    'max_attempts': 3,  # Máximo 3 intentos de pago
}

# Configuración de seguridad
SECURITY_CONFIG = {
    'require_3d_secure': True,
    'require_cvv': True,
    'require_postal_code': True,
    'fraud_detection': True,
}

# Configuración de reportes
REPORTING_CONFIG = {
    'daily_reports': True,
    'weekly_reports': True,
    'monthly_reports': True,
    'report_email': os.getenv('REPORT_EMAIL', 'admin@SmartSales365.com'),
}

# Configuración de desarrollo
DEVELOPMENT_CONFIG = {
    'test_mode': os.getenv('STRIPE_TEST_MODE', 'true').lower() == 'true',
    'test_webhook_endpoint': os.getenv('STRIPE_TEST_WEBHOOK_ENDPOINT', ''),
    'debug_webhooks': os.getenv('STRIPE_DEBUG_WEBHOOKS', 'false').lower() == 'true',
}

# Configuración de producción
PRODUCTION_CONFIG = {
    'webhook_endpoint': os.getenv('STRIPE_WEBHOOK_ENDPOINT', ''),
    'webhook_tolerance': 300,  # 5 minutos
    'retry_failed_webhooks': True,
    'max_retry_attempts': 3,
}
