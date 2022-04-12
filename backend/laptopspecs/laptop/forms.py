import django.forms as forms
from django.utils.translation import gettext_lazy as _

class LaptopForm(forms.Form):
    search_text = forms.CharField(max_length=100, label="Laptop", help_text=_("Enter the laptop name here"))