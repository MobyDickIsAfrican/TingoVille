from django.views.generic import TemplateView
from django_popup_view_field.registry import registry_popup_view

class SizePopupView(TemplateView):
    template_name = 'ecommerce/product-size-select.html'

# REGISTER IS IMPORTANT
registry_popup_view.register(SizePopupView)
