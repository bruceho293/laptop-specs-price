from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic.list import ListView
from django.views.generic import DetailView

from laptop.models import Laptop, Component, Brand
from laptop.forms import LaptopForm

# Create your views here.

def homepage(request):
    laptop_qnty = Laptop.objects.count()
    component_qnty = Component.objects.count()
    brand_qnty = Brand.objects.count()
    return render(request, 'laptop/homepage.html', {
        'laptop_qnty': laptop_qnty,
        'component_qnty': component_qnty,
        'brand_qnty': brand_qnty,
    })

def error_404_not_found(request, exception):
    error_msg = 'Oops! Cannot find the page you are looking for!'
    return render(request, '404.html', {'error_msg': error_msg})

class LaptopSearchList(ListView):
    model = Laptop
    template = 'laptop/laptop_list.html'

    def get_queryset(self):
        name = self.request.GET.get('q')

        return Laptop.objects.filter(name__lower__matchseq=name).order_by('name', 'brand')
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add additional fields
        context['search_text'] = self.request.GET.get('q')
        context['quantity'] = self.get_queryset().count()
        return context
    
    

class LaptopInfo(DetailView):
    model = Laptop
    template = 'laptop/laptop_detail.html'
    pk_url_kwarg = 'laptop_id'
    query_pk_and_slug = True

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        laptop = self.get_object()

        closest_component = {
            'processor': Component.category_manager.get_closest_processor(laptop.processor),
            'memory': Component.category_manager.get_closest_memory_chip(laptop.memory),
            'graphics_card': Component.category_manager.get_closest_graphics_card(laptop.graphics),
            'storage': Component.category_manager.get_closest_storage(laptop.storage) 
        }

        qnty = laptop.qnty.split(',')
        component_qnty = {
            'CPU': int(qnty[0]),
            'RAM': int(qnty[1]),
            'GPU': int(qnty[2]),
            'STR': int(qnty[3]),
        }

        component_per_price = {
            'CPU': closest_component['processor'].get_price if closest_component['processor'] else 0,
            'RAM': closest_component['memory'].get_price if closest_component['memory'] else 0,
            'GPU': closest_component['graphics_card'].get_price if closest_component['graphics_card'] else 0,
            'STR': closest_component['storage'].get_price if closest_component['storage'] else 0,
        }

        component_overall_price = {
            'CPU': component_qnty['CPU'] * float(component_per_price['CPU']),
            'RAM': component_qnty['RAM'] * float(component_per_price['RAM']),
            'GPU': component_qnty['GPU'] * float(component_per_price['GPU']),
            'STR': component_qnty['STR'] * float(component_per_price['STR']),
        }

        total_comps_price = sum(component_overall_price.values())

        price_difference = float(laptop.get_price) - total_comps_price

        no_match_notif = "No Matching Component"

        context['laptop'] = laptop
        context['closest_comp'] = closest_component
        context['no_match_notif'] = no_match_notif
        context['component_qnty'] = component_qnty
        context['component_overall_price'] = component_overall_price
        context['total_comps_price'] = total_comps_price
        context['price_difference'] = price_difference

        return context