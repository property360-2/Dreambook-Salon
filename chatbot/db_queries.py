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
        """Get specific service details by name with fuzzy matching."""
        try:
            # Normalize input and apply synonyms
            synonyms = {
                'coloring': 'color',
                'colouring': 'color',
                'haircut': 'haircut',
                'cut': 'haircut',
                'massage': 'massage',
                'facial': 'facial',
                'manicure': 'manicure',
                'pedicure': 'pedicure',
                'rebond': 'rebond',
                'rebonding': 'rebond',
                'wax': 'waxing',
                'waxing': 'waxing',
            }

            service_name_lower = service_name.lower().strip()

            # Apply synonyms
            for synonym, replacement in synonyms.items():
                if synonym in service_name_lower:
                    service_name_lower = service_name_lower.replace(synonym, replacement)

            # Try exact/contains match first (with normalized name)
            service = Service.objects.filter(
                Q(name__icontains=service_name_lower) & Q(is_active=True)
            ).prefetch_related('features').first()

            # If not found, try original name
            if not service:
                service = Service.objects.filter(
                    Q(name__icontains=service_name) & Q(is_active=True)
                ).prefetch_related('features').first()

            # If still not found, try word-based fuzzy match with OR logic
            if not service:
                words = service_name_lower.split()
                # Build OR query for significant words
                word_query = Q()
                for word in words:
                    if len(word) > 3:  # Only match meaningful words (4+ chars)
                        word_query |= Q(name__icontains=word)

                if word_query:
                    # Get all matches and rank by number of matching words
                    matches = Service.objects.filter(
                        word_query & Q(is_active=True)
                    ).prefetch_related('features')

                    # Score each match by how many search words it contains
                    best_match = None
                    best_score = 0
                    for match in matches:
                        score = sum(1 for word in words if len(word) > 3 and word in match.name.lower())
                        if score > best_score:
                            best_score = score
                            best_match = match

                    service = best_match

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
    def get_appointment_status(user_id: Optional[int], appointment_id: Optional[int] = None, user_role: str = 'CUSTOMER') -> Dict[str, Any]:
        """
        Get appointment details.

        Args:
            user_id: The user requesting appointments
            appointment_id: Specific appointment ID (optional)
            user_role: User's role ('ADMIN', 'STAFF', 'CUSTOMER')

        Returns:
            Appointment data (customers only see their own, staff/admin see all)
        """
        try:
            if appointment_id:
                # Build base query
                if user_role in ['ADMIN', 'STAFF']:
                    # Staff and Admin can see any appointment
                    appointment = Appointment.objects.filter(
                        id=appointment_id
                    ).select_related('service', 'customer').first()
                else:
                    # Customers can only see their own appointments
                    appointment = Appointment.objects.filter(
                        id=appointment_id,
                        customer_id=user_id  # CRITICAL SECURITY FILTER
                    ).select_related('service').first()

                if not appointment:
                    return {"found": False, "message": "Appointment not found"}

                result = {
                    "found": True,
                    "id": appointment.id,
                    "service": appointment.service.name,
                    "date_time": appointment.start_at.strftime('%B %d, %Y at %I:%M %p'),
                    "status": appointment.get_status_display(),
                    "payment_status": appointment.get_payment_state_display(),
                }

                # Include customer info for staff/admin
                if user_role in ['ADMIN', 'STAFF']:
                    result['customer_name'] = appointment.customer.get_full_name() or appointment.customer.email
                    result['customer_email'] = appointment.customer.email

                return result
            else:
                # List appointments
                if user_role in ['ADMIN', 'STAFF']:
                    # Staff and Admin can see all appointments
                    appointments = Appointment.objects.all().select_related('service', 'customer').order_by('-start_at')[:10]
                else:
                    # Customers only see their own
                    if not user_id:
                        return {"found": False, "message": "You must be logged in to view appointments"}

                    appointments = Appointment.objects.filter(
                        customer_id=user_id
                    ).select_related('service').order_by('-start_at')[:5]

                result_list = []
                for a in appointments:
                    appt_data = {
                        "id": a.id,
                        "service": a.service.name,
                        "date_time": a.start_at.strftime('%B %d, %Y at %I:%M %p'),
                        "status": a.get_status_display(),
                        "payment_status": a.get_payment_state_display(),
                    }

                    # Include customer info for staff/admin
                    if user_role in ['ADMIN', 'STAFF']:
                        appt_data['customer_name'] = a.customer.get_full_name() or a.customer.email
                        appt_data['customer_email'] = a.customer.email

                    result_list.append(appt_data)

                return {
                    "found": True,
                    "appointments": result_list,
                    "count": len(result_list)
                }
        except Exception as e:
            return {"error": str(e), "found": False}

    @staticmethod
    def get_revenue_analytics(days: int = 30, user_role: str = 'CUSTOMER') -> Dict[str, Any]:
        """
        Get revenue analytics (staff and admin only).

        Args:
            days: Number of days to analyze
            user_role: User's role ('ADMIN', 'STAFF', 'CUSTOMER')

        Returns:
            Revenue data or access denial
        """
        # Permission check
        if user_role not in ['ADMIN', 'STAFF']:
            return {
                "error": "Permission denied",
                "message": "Sorry, only staff and administrators can access revenue information. Please contact management for assistance."
            }

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
    def get_appointment_analytics(days: int = 30, user_role: str = 'CUSTOMER') -> Dict[str, Any]:
        """
        Get appointment statistics (staff and admin only).

        Args:
            days: Number of days to analyze
            user_role: User's role ('ADMIN', 'STAFF', 'CUSTOMER')

        Returns:
            Appointment analytics or access denial
        """
        # Permission check
        if user_role not in ['ADMIN', 'STAFF']:
            return {
                "error": "Permission denied",
                "message": "Sorry, only staff and administrators can access appointment analytics. Please contact management for assistance."
            }

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
    def get_inventory_status(user_role: str = 'CUSTOMER') -> Dict[str, Any]:
        """
        Get current inventory/stock status (staff and admin only).

        Args:
            user_role: User's role ('ADMIN', 'STAFF', 'CUSTOMER')

        Returns:
            Inventory data or access denial
        """
        # Permission check
        if user_role not in ['ADMIN', 'STAFF']:
            return {
                "error": "Permission denied",
                "message": "Sorry, only staff and administrators can access inventory information. Please contact management for assistance."
            }

        try:
            items = Item.objects.all().values('name', 'stock', 'unit', 'threshold')

            # Calculate low stock items
            low_stock_items = []
            all_items = []
            for item in items:
                is_low = item['stock'] <= item['threshold']
                item_data = {
                    'name': item['name'],
                    'stock': item['stock'],
                    'unit': item['unit'],
                    'threshold': item['threshold'],
                    'is_low_stock': is_low
                }
                all_items.append(item_data)
                if is_low:
                    low_stock_items.append(item_data)

            # Both STAFF and ADMIN see full details
            return {
                "total_items": len(all_items),
                "low_stock_count": len(low_stock_items),
                "low_stock_items": low_stock_items,
                "all_items": all_items
            }
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def get_staff_list(user_role: str = 'CUSTOMER') -> Dict[str, Any]:
        """
        Get list of staff members (staff and admin only).

        Args:
            user_role: User's role ('ADMIN', 'STAFF', 'CUSTOMER')

        Returns:
            Staff list or access denial
        """
        # Permission check
        if user_role not in ['ADMIN', 'STAFF']:
            return {
                "error": "Permission denied",
                "message": "Sorry, only staff and administrators can access staff information. Please contact management for assistance."
            }

        try:
            staff_members = User.objects.filter(
                role__in=['STAFF', 'ADMIN']
            ).values('id', 'first_name', 'last_name', 'email', 'role')

            return {
                "staff_count": len(staff_members),
                "staff_members": list(staff_members)
            }
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def get_tools_dict(user_role: str = 'CUSTOMER') -> Dict[str, callable]:
        """
        Return dictionary of all available tools for the chatbot.
        Tools are role-aware and will enforce permissions.

        Args:
            user_role: The user's role ('ADMIN', 'STAFF', 'CUSTOMER')
        """
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
            'my_appointments': lambda entities: ChatbotDBQueries.get_appointment_status(
                user_id=entities.get('user_id'),
                user_role=user_role
            ),
            'all_appointments': lambda entities: ChatbotDBQueries.get_appointment_status(
                user_id=None,  # No specific user - get all
                user_role=user_role
            ),
            'revenue_analytics': lambda entities: ChatbotDBQueries.get_revenue_analytics(
                days=entities.get('days', 30),
                user_role=user_role
            ),
            'appointment_analytics': lambda entities: ChatbotDBQueries.get_appointment_analytics(
                days=entities.get('days', 30),
                user_role=user_role
            ),
            'inventory_status': lambda entities: ChatbotDBQueries.get_inventory_status(
                user_role=user_role
            ),
            'staff_list': lambda entities: ChatbotDBQueries.get_staff_list(
                user_role=user_role
            ),
        }
