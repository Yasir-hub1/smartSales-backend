"""
Servicios para notificaciones push móviles usando Expo Push Notifications
"""
import requests
import logging
from django.conf import settings
from typing import List, Dict, Optional
from apps.mobile.models import PushNotificationDevice

logger = logging.getLogger(__name__)

# URL de la API de Expo Push Notifications
EXPO_PUSH_API_URL = 'https://exp.host/--/api/v2/push/send'


class ExpoPushNotificationService:
    """Servicio para enviar notificaciones push usando Expo"""
    
    @staticmethod
    def send_notification(
        device_token: str,
        title: str,
        message: str,
        data: Optional[Dict] = None,
        sound: str = 'default',
        priority: str = 'default',
        channel_id: str = 'default'
    ) -> Dict:
        """
        Envía una notificación push a un dispositivo
        
        Args:
            device_token: Token del dispositivo Expo
            title: Título de la notificación
            message: Mensaje de la notificación
            data: Datos adicionales para la notificación
            sound: Sonido de la notificación
            priority: Prioridad ('default' o 'high')
            channel_id: ID del canal (para Android)
            
        Returns:
            Dict con resultado del envío
        """
        try:
            notification = {
                'to': device_token,
                'title': title,
                'body': message,
                'sound': sound,
                'priority': priority,
                'channelId': channel_id,
                'data': data or {},
            }
            
            response = requests.post(
                EXPO_PUSH_API_URL,
                json=notification,
                headers={
                    'Accept': 'application/json',
                    'Accept-Encoding': 'gzip, deflate',
                    'Content-Type': 'application/json',
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('data', {}).get('status') == 'ok':
                    logger.info(f'Notificación enviada exitosamente a {device_token[:20]}...')
                    return {'success': True, 'message': 'Notificación enviada'}
                else:
                    error_message = result.get('data', {}).get('message', 'Error desconocido')
                    logger.error(f'Error enviando notificación: {error_message}')
                    return {'success': False, 'message': error_message}
            else:
                logger.error(f'Error HTTP al enviar notificación: {response.status_code}')
                return {'success': False, 'message': f'Error HTTP {response.status_code}'}
                
        except requests.exceptions.Timeout:
            logger.error('Timeout al enviar notificación push')
            return {'success': False, 'message': 'Timeout al enviar notificación'}
        except requests.exceptions.RequestException as e:
            logger.error(f'Error de conexión al enviar notificación: {str(e)}')
            return {'success': False, 'message': f'Error de conexión: {str(e)}'}
        except Exception as e:
            logger.error(f'Error inesperado al enviar notificación: {str(e)}', exc_info=True)
            return {'success': False, 'message': f'Error inesperado: {str(e)}'}
    
    @staticmethod
    def send_multiple_notifications(
        notifications: List[Dict]
    ) -> Dict:
        """
        Envía múltiples notificaciones en un solo request
        
        Args:
            notifications: Lista de diccionarios con formato de notificación
            
        Returns:
            Dict con resultado del envío
        """
        try:
            response = requests.post(
                EXPO_PUSH_API_URL,
                json=notifications,
                headers={
                    'Accept': 'application/json',
                    'Accept-Encoding': 'gzip, deflate',
                    'Content-Type': 'application/json',
                },
                timeout=30
            )
            
            if response.status_code == 200:
                results = response.json()
                success_count = sum(
                    1 for r in results.get('data', [])
                    if r.get('status') == 'ok'
                )
                total = len(results.get('data', []))
                
                logger.info(f'Notificaciones enviadas: {success_count}/{total}')
                return {
                    'success': True,
                    'sent': success_count,
                    'total': total,
                    'results': results
                }
            else:
                logger.error(f'Error HTTP al enviar notificaciones: {response.status_code}')
                return {'success': False, 'message': f'Error HTTP {response.status_code}'}
                
        except Exception as e:
            logger.error(f'Error al enviar notificaciones múltiples: {str(e)}', exc_info=True)
            return {'success': False, 'message': f'Error: {str(e)}'}
    
    @staticmethod
    def send_to_user_devices(
        user_id: int,
        title: str,
        message: str,
        data: Optional[Dict] = None,
        notification_type: str = 'info'
    ) -> Dict:
        """
        Envía notificación a todos los dispositivos activos de un usuario
        
        Args:
            user_id: ID del usuario
            title: Título de la notificación
            message: Mensaje de la notificación
            data: Datos adicionales
            notification_type: Tipo de notificación ('info', 'warning', 'success', 'error')
            
        Returns:
            Dict con resultado del envío
        """
        devices = PushNotificationDevice.objects.filter(
            user_id=user_id,
            is_active=True
        )
        
        if not devices.exists():
            logger.warning(f'No hay dispositivos activos para el usuario {user_id}')
            return {'success': False, 'message': 'No hay dispositivos activos'}
        
        sent_count = 0
        failed_count = 0
        notifications = []
        
        for device in devices:
            notification_data = {
                'type': notification_type,
                'user_id': user_id,
                **(data or {})
            }
            
            notifications.append({
                'to': device.device_token,
                'title': title,
                'body': message,
                'sound': 'default',
                'priority': 'high' if notification_type in ['warning', 'error'] else 'default',
                'channelId': 'default',
                'data': notification_data,
            })
        
        # Enviar todas las notificaciones
        result = ExpoPushNotificationService.send_multiple_notifications(notifications)
        
        # Actualizar timestamp de última notificación
        from django.utils import timezone
        devices.update(last_notification_sent=timezone.now())
        
        if result.get('success'):
            sent_count = result.get('sent', 0)
            failed_count = result.get('total', 0) - sent_count
        
        return {
            'success': result.get('success', False),
            'sent': sent_count,
            'failed': failed_count,
            'total': len(notifications)
        }
    
    @staticmethod
    def send_to_all_users(
        title: str,
        message: str,
        data: Optional[Dict] = None,
        notification_type: str = 'info'
    ) -> Dict:
        """
        Envía notificación a todos los usuarios con dispositivos activos
        
        Args:
            title: Título de la notificación
            message: Mensaje de la notificación
            data: Datos adicionales
            notification_type: Tipo de notificación
            
        Returns:
            Dict con resultado del envío
        """
        devices = PushNotificationDevice.objects.filter(is_active=True)
        
        if not devices.exists():
            logger.warning('No hay dispositivos activos')
            return {'success': False, 'message': 'No hay dispositivos activos', 'sent': 0, 'failed': 0}
        
        sent_count = 0
        failed_count = 0
        notifications = []
        
        for device in devices:
            notification_data = {
                'type': notification_type,
                'user_id': device.user_id,
                **(data or {})
            }
            
            notifications.append({
                'to': device.device_token,
                'title': title,
                'body': message,
                'sound': 'default',
                'priority': 'high' if notification_type in ['warning', 'error'] else 'default',
                'channelId': 'default',
                'data': notification_data,
            })
        
        # Enviar en lotes de 100 (límite de Expo)
        batch_size = 100
        total_batches = (len(notifications) + batch_size - 1) // batch_size
        
        for i in range(0, len(notifications), batch_size):
            batch = notifications[i:i + batch_size]
            result = ExpoPushNotificationService.send_multiple_notifications(batch)
            
            if result.get('success'):
                sent_count += result.get('sent', 0)
                failed_count += (result.get('total', 0) - result.get('sent', 0))
            else:
                failed_count += len(batch)
        
        # Actualizar timestamp de última notificación
        from django.utils import timezone
        devices.update(last_notification_sent=timezone.now())
        
        return {
            'success': True,
            'sent': sent_count,
            'failed': failed_count,
            'total': len(notifications)
        }

