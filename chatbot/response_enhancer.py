"""
Response Enhancer Module for Intelligent Chatbot
Adds validation, source-awareness, confidence levels, and actionable next steps
"""

from datetime import datetime
from services.models import Service
from appointments.models import Appointment
from payments.models import Payment
from inventory.models import Item
import re


class ResponseEnhancer:
    """Enhances chatbot responses with validation and source-awareness"""

    def __init__(self, user=None):
        self.user = user
        self.is_staff = user and user.is_authenticated and user.role in ['ADMIN', 'STAFF']
        self.confidence_level = "high"

    def validate_date_input(self, date_str):
        """Validate date input with multiple format support"""
        if not date_str or not isinstance(date_str, str):
            return None, "Please provide a date in format MM/DD/YYYY"

        date_str = date_str.strip()
        formats = ['%m/%d/%Y', '%m-%d-%Y', '%d/%m/%Y', '%d-%m-%Y', '%m/%d/%y', '%m-%d-%y']

        for fmt in formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt).date()
                return parsed_date, None
            except ValueError:
                continue

        return None, f"Date format '{date_str}' not recognized. Use MM/DD/YYYY format."

    def validate_service_name(self, service_name):
        """Validate and search for service by name"""
        if not service_name or len(service_name.strip()) < 2:
            return None, "Service name too short", None

        search_term = service_name.strip()
        service = Service.objects.filter(name__iexact=search_term, is_active=True).first()

        if service:
            return service, None, "Found in active services"

        service = Service.objects.filter(name__icontains=search_term, is_active=True).first()
        if service:
            return service, None, "Found similar service"

        available = Service.objects.filter(is_active=True).values_list('name', flat=True)[:5]
        suggestions = ", ".join(available) if available else "Check services page"
        error_msg = f"Service '{service_name}' not found. Available: {suggestions}"

        return None, error_msg, None

    def add_source_citation(self, response, count=None, data_date=None):
        """Add source citation to response"""
        if not count and not data_date:
            return response

        citation = "\n\n*Source: "
        if count is not None:
            citation += f"Based on {count} records"
        if data_date:
            citation += f" (as of {data_date.strftime('%B %d, %Y')})"
        citation += "*"

        return response + citation

    def create_friendly_error(self, error_msg, suggestions=None):
        """Create friendly error response"""
        response = f"😔 {error_msg}"
        if suggestions:
            response += "\n\n**Suggestions:**\n"
            for suggestion in suggestions:
                response += f"• {suggestion}\n"
        return response