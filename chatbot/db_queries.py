"""
Database Query Handler for Intelligent Chatbot
Provides functions to query appointment, service, and business data
"""
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta
from typing import Dict, List, Any, Optional

from services.models import Service, ServiceFeature
from appointments.models import Appointment, AppointmentSettings
from payments.models import Payment
from inventory.models import Item
from core.models import User


class ChatbotDBQueries:
    """Database query helper for chatbot operations."""

    @staticmethod
    def get_all_services(limit: int = 10) -> Dict[str, Any]:
        """Get list of available services with pricing."""
        try:
            services = Service.objects.filter(
                is_active=True
            ).prefetch_related('features').values(
                'id', 'name', 'price', 'duration_minutes', 'description'
            )[:limit]

            result = {
                "services": list(services),
                "count": len(services)
            }

            # Add features for each service
            for service in result["services"]:
                service_obj = Service.objects.get(id=service['id'])
                service['features'] = [f.name for f in service_obj.features.all()]

            return result
        except Exception as e:
            return {"error": str(e), "services": []}

    @staticmethod
    def get_service_by_name(service_name: str) -> Dict[str, Any]:
        """Get specific service details by name."""
        try:
            service = Service.objects.filter(
                Q(name__icontains=service_name) & Q(is_active=True)
            ).prefetch_related('features').first()

            if not service:
                return {
                    "found": False,
                    "message": f"Service '{service_name}' not found"
                }

            features = [f.name for f in service.features.all()]

            return {
                "found": True,
                "id": service.id,
                "name": service.name,
                "price": str(service.price),
                "duration": f"{service.duration_minutes} minutes",
                "description": service.description,
                "features": features,
                "requires_downpayment": service.requires_downpayment,
                "downpayment_amount": str(service.downpayment_amount) if service.requires_downpayment else None,
            }
        except Exception as e:
            return {"error": str(e), "found": False}

    @staticmethod
    def check_availability(service_id: Optional[int] = None, date_str: Optional[str] = None, time_str: Optional[str] = None) -> Dict[str, Any]:
        """Check appointment availability for a service."""
        try:
            from appointments.views import check_availability as check_avail_func
            from datetime import datetime

            if not service_id or not date_str or not time_str:
                return {
                    "available": False,
                    "message": "Missing service_id, date, or time"
                }

            service = Service.objects.get(id=service_id, is_active=True)

            try:
                # Parse date and time
                booking_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                booking_time = datetime.strptime(time_str, '%H:%M').time()
                start_at = timezone.make_aware(datetime.combine(booking_date, booking_time))
            except ValueError:
                return {
                    "available": False,
                    "message": "Invalid date or time format"
                }

            is_available, reason = check_avail_func(service, start_at)

            return {
                "available": is_available,
                "service": service.name,
                "requested_time": f"{date_str} {time_str}",
                "reason_if_unavailable": reason if not is_available else None,
                "message": "This time slot is available! 📅" if is_available else f"Unavailable: {reason}"
            }
        except Service.DoesNotExist:
            return {"available": False, "message": "Service not found"}
        except Exception as e:
            return {"error": str(e), "available": False}

    @staticmethod
    def get_popular_services(limit: int = 5) -> Dict[str, Any]:
        """Get most booked/popular services."""
        try:
            popular = Service.objects.filter(
                is_active=True
            ).annotate(
                booking_count=Count('appointments')
            ).order_by('-booking_count').values(
                'id', 'name', 'price', 'booking_count'
            )[:limit]

            return {
                "popular_services": list(popular),
                "count": len(popular)
            }
        except Exception as e:
            return {"error": str(e), "popular_services": []}

    @staticmethod
    def get_business_hours() -> Dict[str, Any]:
        """Get business hours and contact info."""
        try:
            from chatbot.models import ChatbotConfig

            config = ChatbotConfig.objects.first() or ChatbotConfig()

            return {
                "business_hours": config.business_hours,
                "location": config.location,
                "phone": config.contact_phone,
                "email": config.contact_email,
                "max_daily_appointments": config.max_daily_appointments
            }
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def get_appointment_status(user_id: int, appointment_id: Optional[int] = None) -> Dict[str, Any]:
        """Get appointment details for a customer."""
        try:
            if appointment_id:
                appointment = Appointment.objects.filter(
                    id=appointment_id,
                    customer_id=user_id
                ).select_related('service').first()

                if not appointment:
                    return {"found": False, "message": "Appointment not found"}

                return {
                    "found": True,
                    "id": appointment.id,
                    "service": appointment.service.name,
                    "date_time": appointment.start_at.strftime('%B %d, %Y at %I:%M %p'),
                    "status": appointment.get_status_display(),
                    "payment_status": appointment.get_payment_state_display(),
                }
            else:
                appointments = Appointment.objects.filter(
                    customer_id=user_id
                ).select_related('service').order_by('-start_at')[:5]

                return {
                    "found": True,
                    "appointments": [
                        {
                            "id": a.id,
                            "service": a.service.name,
                            "date_time": a.start_at.strftime('%B %d, %Y at %I:%M %p'),
                            "status": a.get_status_display(),
                            "payment_status": a.get_payment_state_display(),
                        }
                        for a in appointments
                    ],
                    "count": len(appointments)
                }
        except Exception as e:
            return {"error": str(e), "found": False}

    @staticmethod
    def get_revenue_analytics(days: int = 30) -> Dict[str, Any]:
        """Get revenue analytics (staff only)."""
        try:
            since_date = timezone.now() - timedelta(days=days)

            total_revenue = Payment.objects.filter(
                created_at__gte=since_date,
                status='paid'
            ).aggregate(Sum('amount'))['amount__sum'] or 0

            daily_stats = []
            for i in range(days):
                date = timezone.now().date() - timedelta(days=i)
                day_revenue = Payment.objects.filter(
                    created_at__date=date,
                    status='paid'
                ).aggregate(Sum('amount'))['amount__sum'] or 0

                daily_stats.append({
                    "date": str(date),
                    "revenue": str(day_revenue)
                })

            return {
                "total_revenue": str(total_revenue),
                "period_days": days,
                "daily_breakdown": daily_stats[:7],  # Last 7 days
                "currency": "₱"
            }
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def get_appointment_analytics(days: int = 30) -> Dict[str, Any]:
        """Get appointment statistics (staff only)."""
        try:
            since_date = timezone.now() - timedelta(days=days)

            total_appointments = Appointment.objects.filter(
                created_at__gte=since_date
            ).count()

            completed = Appointment.objects.filter(
                created_at__gte=since_date,
                status='completed'
            ).count()

            pending = Appointment.objects.filter(
                created_at__gte=since_date,
                status__in=['pending', 'confirmed']
            ).count()

            no_show = Appointment.objects.filter(
                created_at__gte=since_date,
                status='no_show'
            ).count()

            return {
                "total": total_appointments,
                "completed": completed,
                "pending": pending,
                "no_show": no_show,
                "completion_rate": f"{(completed/total_appointments*100):.1f}%" if total_appointments > 0 else "0%",
                "period_days": days
            }
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def get_inventory_status() -> Dict[str, Any]:
        """Get current inventory/stock status."""
        try:
            items = Item.objects.all().values('name', 'stock', 'unit', 'is_low_stock')

            low_stock_items = [item for item in items if item['is_low_stock']]

            return {
                "total_items": len(items),
                "low_stock_count": len(low_stock_items),
                "low_stock_items": low_stock_items,
                "all_items": list(items)
            }
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def get_tools_dict() -> Dict[str, callable]:
        """Return dictionary of all available tools for the chatbot."""
        return {
            'list_services': lambda entities: ChatbotDBQueries.get_all_services(),
            'get_pricing': lambda entities: ChatbotDBQueries.get_service_by_name(
                entities.get('service_name', '')
            ) if entities.get('service_name') else ChatbotDBQueries.get_all_services(),
            'check_availability': lambda entities: ChatbotDBQueries.check_availability(
                service_id=entities.get('service_id'),
                date_str=entities.get('date'),
                time_str=entities.get('time')
            ),
            'popular_services': lambda entities: ChatbotDBQueries.get_popular_services(),
            'business_hours': lambda entities: ChatbotDBQueries.get_business_hours(),
            'appointment_status': lambda entities: ChatbotDBQueries.get_appointment_status(
                user_id=entities.get('user_id')
            ),
            'revenue_analytics': lambda entities: ChatbotDBQueries.get_revenue_analytics(
                days=entities.get('days', 30)
            ),
            'appointment_analytics': lambda entities: ChatbotDBQueries.get_appointment_analytics(
                days=entities.get('days', 30)
            ),
            'inventory_status': lambda entities: ChatbotDBQueries.get_inventory_status(),
        }
