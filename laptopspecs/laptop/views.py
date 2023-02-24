from django.shortcuts import get_object_or_404, render
from django.views.generic.list import ListView
from django.views.generic import DetailView
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from rest_framework import viewsets, permissions, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action

from laptop.models import Laptop, Component, Brand
from laptop.serializers import LaptopSerializer, LaptopDetailSerializer, ComponentSerializer, ComponentListSerializer, BrandSerializer
from laptop.utils import get_memo_with_component_qnty, get_closest_components, get_closest_components_price, update_price_difference

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

        # Get the laptop and its memos
        laptop = self.get_object()
        qnty_memos = get_memo_with_component_qnty(laptop=laptop)
        cpu, ram, gpu, disk = qnty_memos

        memos = {
            'cpu': cpu,
            'ram': ram,
            'gpu': gpu,
            'disk': disk
        }

        closest_components = get_closest_components(qnty_memo=qnty_memos)

        total_comps_price = get_closest_components_price(closest_components=closest_components)
              
        price_difference = update_price_difference(laptop=laptop, total_comps_price=total_comps_price)

        no_match_notif = "No Matching Component"

        context['laptop'] = laptop
        context['memos'] = memos
        context['closest_comp'] = closest_components
        context['no_match_notif'] = no_match_notif
        context['total_comps_price'] = total_comps_price
        context['price_difference'] = price_difference

        return context

# REST API 
class BrandLogoList(generics.ListAPIView):
    queryset = Brand.objects.all().order_by('name')
    serializer_class = BrandSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    paginator = None

class LaptopViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Laptop.objects.all().order_by('name')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'

    @method_decorator(cache_page(60*30))
    def list(self, request):
        serializer = LaptopSerializer(self.queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @method_decorator(cache_page(60*30))
    def retrieve(self, request, slug=None):
        laptop = get_object_or_404(self.queryset, slug=slug)
        update_price_difference(laptop=laptop)
        serializer = LaptopDetailSerializer(laptop)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @method_decorator(cache_page(60*30))
    @action(detail=True, url_path='get-matching-components')
    def get_matching_components(self, request, slug=None):
        laptop = get_object_or_404(self.queryset, slug=slug)
        
        cpu, ram, gpu, disk = get_memo_with_component_qnty(laptop=laptop)

        values = ('name', 'category', 'brand__name', 'link', 'updated', 'total_price', 'comp_count')

        matching_cpu = Component.category_manager.get_closest_processor(cpu).values(*values)
        matching_ram = Component.category_manager.get_closest_memory_chip(ram).values(*values)
        matching_gpu = Component.category_manager.get_closest_graphics_card(gpu).values(*values)
        matching_disk = Component.category_manager.get_closest_storage(disk).values(*values)
        
        matching_components = matching_cpu.union(matching_ram, matching_gpu, matching_disk)

        serializer = ComponentListSerializer(matching_components, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ComponentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Component.objects.all().order_by('name')
    serializer_class = ComponentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]