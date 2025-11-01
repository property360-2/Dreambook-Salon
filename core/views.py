from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "featured_services": [
                    {
                        "name": "Precision Haircut",
                        "description": "Tailored cuts with relaxing wash and finish.",
                        "duration": "45 mins",
                        "price": "₱850",
                    },
                    {
                        "name": "Color & Gloss",
                        "description": "Vibrant color application with gloss sealing.",
                        "duration": "90 mins",
                        "price": "₱2,300",
                    },
                    {
                        "name": "Spa Manicure",
                        "description": "Nail shaping, cuticle care, and polish.",
                        "duration": "40 mins",
                        "price": "₱650",
                    },
                ],
                "inventory_highlights": [
                    {
                        "name": "Argan Oil Serum",
                        "status": "In stock",
                        "badge": "core",
                    },
                    {
                        "name": "Keratin Treatment Kit",
                        "status": "Low stock",
                        "badge": "warning",
                    },
                ],
            }
        )
        return context
