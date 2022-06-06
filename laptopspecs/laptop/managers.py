from django.db import models
from django.db.models import Field, Lookup, Transform, CharField
from django.db.models import QuerySet, FloatField, TextField
from django.db.models import F, Value, Case, When, ExpressionWrapper
from django.db.models.functions import Cast, Round
from django.utils.translation import gettext_lazy as _
from django.db import connection

from common.util.regex_matching import text_to_seq_pattern
from common.util.unit import unit_conversion

from laptop.functions import SubStrRegex

class LowerCase(Transform):
    lookup_name = 'lower'
    function = 'LOWER'
    bilateral = True

TextField.register_lookup(LowerCase)
CharField.register_lookup(LowerCase)

@Field.register_lookup
class MatchInSensitiveCommonSequence(Lookup):
    lookup_name = 'matchseq'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler=compiler, connection=connection)
        rhs, rhs_params = self.process_rhs(compiler=compiler, connection=connection)

        # Replace SPACE character with '%' for the RHS params
        rhs_params[0] = '{}{}{}'.format('%', rhs_params[0].replace(' ', '%'), '%')

        params = lhs_params + rhs_params
        return '%s LIKE %s' % (lhs, rhs), params


class ComponentType(models.TextChoices):
    CPU = 'CPU', _("Processor")
    GPU = 'GPU', _("Graphics Card")
    RAM = 'RAM', _("Memory")
    DISK = 'DISK', _("Storage")

class CategoryQuerySet(models.QuerySet):
    def processor(self):
        return self.filter(category=ComponentType.CPU)

    def graphics_card(self):
        return self.filter(category=ComponentType.GPU)

    def memory(self):
        return self.filter(category=ComponentType.RAM)

    def storage(self):
        return self.filter(category=ComponentType.DISK) 

class CategoryManager(models.Manager):
    def get_queryset(self):
        return CategoryQuerySet(model=self.model, using=self._db)
    
    def get_processors(self):
        return self.get_queryset().processor()
    
    def get_graphics_cards(self):
        return self.get_queryset().graphics_card()

    def get_memory_chips(self):
        return self.get_queryset().memory()

    def get_storages(self):
        return self.get_queryset().storage()

    '''
        Get the "closest" associated components based on the name
        of the components recorded from the laptop's attributes.
        "Closest" means the component would have similar/identical name
        compared to the names/descriptions in the memos given from the laptop with 
        the lowest possible price. If there's no matches, return the component
        in the same category with the lowest price 
    '''
    def get_closest_processor(self, memo):
        return get_matching_component(queryset=self.get_processors(), memo=memo)
    
    def get_closest_graphics_card(self, memo):
        return get_matching_component(queryset=self.get_graphics_cards(), memo=memo)
    
    def get_closest_memory_chip(self, memo):
        return get_matching_component(queryset=self.get_memory_chips(), memo=memo)
    
    def get_closest_storage(self, memo):
        return get_matching_component(queryset=self.get_storages(), memo=memo)


def get_matching_component(queryset: CategoryQuerySet, memo: QuerySet):
    # memo: a QuerySet of Memo model
    # Extra fields:
    #     qnty - the quantity of the component/memo (1 type of component) associated with the laptop.

    # Set up the set of matching components
    component = None
    # Check if the component has capacity
    has_capacity = memo[0].has_capacity
    # Prepare Regex pattern for components having capacity
    CAPACITY_REGEX = '^[0-9]{1,3} [TGM]B'
    UNIT_SIZE_REGEX = '^[0-9]{1,3}'
    UNIT_REGEX = '[TGM]B'
 
    if has_capacity:
        for comp_memo in memo:
            # Get the true name of the component after extracting the capacity 
            name = comp_memo.get_true_name
            qnty = comp_memo.qnty
            words = name.split(" ")
            length = len(words)
            
            # Check if the any matching component based on both capacity and quantity
            #     Ex: 4 GB <name of the memory card> with qnty = 2
            #         Step 1: Check if there exists a component matching the name that has capacity 4 GB.
            #            If yes, return the matching component, if not move to Step 2.
            #         Step 2: Similar to Step 1 but the capacity is now 8 GB.
            #            Qnty decrease: 2 --> 1
            size_in_int, capacity_unit = comp_memo.get_capacity
            
            # Get all the component that can be matched based on capacity compatibility. 
            # Use CASE WHEN in Django ORM with Alias()
            # 
            # In PostgreSQL Reference Query if the capacity in the memo is  8 GB
            #   
            #       WITH capacity_comp AS (
            #       	SELECT *, 
            #               CASE 
            #                   WHEN SUBSTRING(name, 1, 6) ~ '^[0-9]{1,3} [TGM]B' THEN SUBSTRING(name, '^[0-9]{1,3} [TGM]B')
            #       	        ELSE 'No capacity'
            #               END AS Capacity
            #           FROM laptop_component
            #           WHERE category='RAM'
            #       ), convert_comp AS (
            #       	SELECT CC.name, 
            #       	    CAST(SUBSTRING(CC.Capacity, '^[0-9]{1,3}') AS INTEGER) AS storage_size,
            #       	    CASE
            #       	        WHEN SUBSTRING(CC.Capacity, '[TGM]B') ~ 'GB' THEN '1000'::integer
            #       	        WHEN SUBSTRING(CC.Capacity, '[TGM]B') ~ 'TB' THEN '1000000'::integer
            #       	        ELSE '1'::integer
            #       	    END AS unit_conversion
            #       	FROM capacity_comp CC
            #       )
            #       SELECT C_C.name, 
            #           C_C.storage_size,
            #           C_C.unit_conversion,
            #       	C_C.storage_size * C_C.unit_conversion / (8::numeric * 1000) as comp_count
            #       FROM convert_comp C_C;

            capa_qs = queryset.alias(capacity=SubStrRegex('name', Value(CAPACITY_REGEX))) \
                .annotate(
                    # Create fields to store the unit size and the capacity unit
                    unit_size=Cast(SubStrRegex('capacity', Value(UNIT_SIZE_REGEX)), output_field=FloatField()), 
                    unit=SubStrRegex('capacity', Value(UNIT_REGEX), output_field=TextField())) \
                .annotate(
                    # Convert the value of the unit accordingly
                    unit_in_num=Case(
                        When(unit__iexact='TB', then=Value(10**6, output_field=FloatField())),
                        When(unit__iexact='GB', then=Value(10**3, output_field=FloatField())),
                        default=Value(1, output_field=FloatField())
                    )
                ) \
                .annotate(
                    # Get the calculated count of the component compared to the that specific memo
                    comp_count=ExpressionWrapper(
                        (Value(size_in_int, output_field=FloatField()) / F('unit_size'))
                        * 
                        (Value(unit_conversion(capacity_unit), output_field=FloatField()) / F('unit_in_num'))
                    ,output_field=FloatField())
                ) \
                .filter(
                    #  Only collect the appropriate component
                    comp_count__gte=1
                ) \
                .annotate(
                    # Update each component with the new count and Calculate the total price
                    comp_count=Round(F('comp_count') * Value(qnty), output_field=FloatField()),
                    total_price=ExpressionWrapper(Round(F('comp_count') * Value(qnty), output_field=FloatField()) * F('price'), output_field=FloatField())
                )
            
            # Get all components based on the true name
            # ATTENTION: need more improvement for performance
            qs = capa_qs.filter(name__lower__matchseq=name).order_by('price')
            while not qs.exists() and length > 0:
                length = length - 1
                new_search_name = " ".join(words[:length])
                qs = capa_qs.filter(name__lower__matchseq=new_search_name).order_by('price')

            # If qs is empty, then increase the size based on the quantity

            qs = qs[:1]
            if component == None:
                component = qs
            else:
                component = component.union(qs)

    else: # When components do not have capacity
        for comp_memo in memo:
            name = comp_memo.get_true_name
            qnty = comp_memo.qnty
            words = name.split(" ")
            length = len(words)
            
            qs = queryset.filter(name__lower__matchseq=name) \
                .annotate(
                    comp_count=Value(qnty),
                    total_price=ExpressionWrapper(Value(qnty) * F('price'), output_field=FloatField())
                ) \
                .order_by('price')
            # ATTENTION: need more improvement for performance
            while not qs.exists() and length > 1:
                length = length - 1
                new_search_name = " ".join(words[:length])
                qs = queryset.filter(name__lower__matchseq=new_search_name) \
                    .annotate(
                        comp_count=Value(qnty),
                        total_price=ExpressionWrapper(Value(qnty) * F('price'), output_field=FloatField())
                        ) \
                    .order_by('price')

            qs = qs[:1]
            if component == None:
                component = qs
            else:
                component = component.union(qs)
    
    return component

    # For MongoDB

    # name_pattern = text_to_seq_pattern(name)
    # regex = re.compile(name_pattern, re.IGNORECASE)

    # if connection.vendor == 'djongo':
    #     return
    # else:
    #     if not queryset.filter(name__iregex=regex.pattern).exists():
    #         return queryset.order_by('price').first()
    #     return queryset.filter(name__iregex=regex.pattern).order_by('price').first()