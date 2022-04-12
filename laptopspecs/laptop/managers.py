from django.db import models
from django.db.models import Field, Lookup, Transform, CharField, TextField
from django.utils.translation import gettext_lazy as _
from django.db import connection

from common.util.regex_matching import text_to_seq_pattern
import re

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
        compared to the names/descriptions given from the laptop with 
        the lowest possible price. If there's no matches, return the component
        in the category with the lowest price 
    '''
    def get_closest_processor(self, name):
        return get_matching_component(queryset=self.get_processors(), name=name)
    
    def get_closest_graphics_card(self, name):
        return get_matching_component(queryset=self.get_graphics_cards(), name=name)
    
    def get_closest_memory_chip(self, name):
        return get_matching_component(queryset=self.get_memory_chips(), name=name)
    
    def get_closest_storage(self, name):
        return get_matching_component(queryset=self.get_storages(), name=name)


def get_matching_component(queryset: CategoryQuerySet, name):
    if not queryset.filter(name__lower__matchseq=name).exists():
        return queryset.order_by('price').first()
    return queryset.filter(name__lower__matchseq=name).order_by('price').first()
    # name_pattern = text_to_seq_pattern(name)
    # regex = re.compile(name_pattern, re.IGNORECASE)

    # if connection.vendor == 'djongo':
    #     return
    # else:
    #     if not queryset.filter(name__iregex=regex.pattern).exists():
    #         return queryset.order_by('price').first()
    #     return queryset.filter(name__iregex=regex.pattern).order_by('price').first()