from django.shortcuts import get_object_or_404, render
from django.views.generic.list import ListView
from django.views.generic import DetailView
from django.db.models import F

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action

from laptop.models import Laptop, Component, Brand, Memo
from laptop.managers import ComponentType
from laptop.serializers import LaptopListSerializer, LaptopDetailSerializer, ComponentSerializer, ComponentListSerializer

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

        # Get the laptop and its memos
        laptop = self.get_object()
        memos = Memo.objects.filter(note_detail__laptop=laptop).annotate(qnty=F('note_detail__qnty')).order_by('name')
        cpu = memos.filter(category=ComponentType.CPU)  
        ram = memos.filter(category=ComponentType.RAM)
        gpu = memos.filter(category=ComponentType.GPU)
        disk = memos.filter(category=ComponentType.DISK)

        memos = {
            'cpu': cpu,
            'ram': ram,
            'gpu': gpu,
            'disk': disk
        }

        closest_component = {
            'processor': Component.category_manager.get_closest_processor(cpu),
            'memory': Component.category_manager.get_closest_memory_chip(ram),
            'graphics_card': Component.category_manager.get_closest_graphics_card(gpu),
            'storage': Component.category_manager.get_closest_storage(disk) 
        }

        total_comps_price = 0
        for category_comp in closest_component.keys():
            components = closest_component[category_comp]
            if components.exists():
                for component in components:
                    count = component.comp_count
                    price = component.get_price
                    total_comps_price += float(price) * count
                

        price_difference = float(laptop.get_price) - total_comps_price

        no_match_notif = "No Matching Component"

        context['laptop'] = laptop
        context['memos'] = memos
        context['closest_comp'] = closest_component
        context['no_match_notif'] = no_match_notif
        context['total_comps_price'] = total_comps_price
        context['price_difference'] = price_difference

        return context

class LaptopViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Laptop.objects.all().order_by('name')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'

    def list(self, request):
        serializer = LaptopListSerializer(self.queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, slug=None):
        laptop = get_object_or_404(self.queryset, slug=slug)
        serializer = LaptopDetailSerializer(laptop)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True)
    def get_matching_components(self, request, slug=None):
        laptop = get_object_or_404(self.queryset, slug=slug)
        
        memos = Memo.objects.filter(note_detail__laptop=laptop).annotate(qnty=F('note_detail__qnty')).order_by('name')
        cpu = memos.filter(category=ComponentType.CPU)  
        ram = memos.filter(category=ComponentType.RAM)
        gpu = memos.filter(category=ComponentType.GPU)
        disk = memos.filter(category=ComponentType.DISK)

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