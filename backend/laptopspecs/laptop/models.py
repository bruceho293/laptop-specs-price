from django.db import models
from django.urls import reverse

from laptop.managers import CategoryManager, ComponentType

#  Create your models here.
class Brand(models.Model):
    name = models.CharField(verbose_name="brand_name", max_length=255, blank=False, null=False)
    link = models.URLField(verbose_name="website", max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name

# Components: Storage, Processor, Memory, Graphics Card
class Component(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False, unique=True)
    category = models.CharField(max_length=5, choices=ComponentType.choices, blank=False, null=False)
    price = models.DecimalField(max_digits=7, decimal_places=2, blank=False)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    link = models.URLField(max_length=255, blank=False, null=False)
    updated = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    category_manager = CategoryManager()

    def __str__(self):
        return self.name
    
    @property
    def get_price(self):
        return self.price

    @property
    def get_source_url(self):
        return self.link


# Laptop
class Laptop(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False, unique=True)
    slug = models.SlugField(max_length=255, null=False, unique=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=7, decimal_places=2, blank=False, null=False)
    link = models.URLField(verbose_name='source', max_length=255, blank=False, null=False)
    updated = models.DateTimeField(auto_now=True)

    processor = models.CharField(max_length=125, blank=False, null=False)
    memory = models.CharField(max_length=125, blank=False, null=False)
    graphics = models.CharField(max_length=125, blank=False, null=False)
    storage = models.CharField(max_length=125, blank=False, null=False)

    qnty = models.CharField(max_length=20, blank=False, null=False, default='1,1,1,1')

    objects = models.Manager()

    def __str__(self):
        return self.name

    @property
    def get_price(self):
        return self.price

    @property
    def get_absolute_url(self):
        return reverse("laptop:laptop-info", kwargs={"laptop_id": self.id, "slug": self.slug})

    @property
    def get_source_url(self):
        return self.link