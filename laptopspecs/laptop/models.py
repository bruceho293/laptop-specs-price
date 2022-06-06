from django.db import models
from django.urls import reverse

from laptop.managers import CategoryManager, ComponentType

#  Create your models here.
class Brand(models.Model):
    name = models.CharField(verbose_name="brand_name", max_length=255, blank=False, null=False)
    link = models.URLField(verbose_name="website", max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name

class Memo(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False, unique=True)
    category = models.CharField(max_length=5, choices=ComponentType.choices, blank=False, null=False)

    def __str__(self):
        return self.name

    @property
    def has_capacity(self):
        return self.category == ComponentType.RAM or self.category == ComponentType.DISK

    @property
    def get_capacity(self):
        # Get the detail capacity of the memory and storage from the name.
        # Input: <size> <unit> <name of the component>
        # Output: <size>, <unit>, <name without capacity>
        inputs = str(self.name).split(' ')
        size, unit = inputs[0], inputs[1]
        return size, unit

    @property
    def get_true_name(self):
        if self.has_capacity:
            words = self.name.split(" ")
            return " ".join(words[2:]) # Ignore the first 2 words describing capacity
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

    @property
    def has_capacity(self):
        return self.category == ComponentType.RAM or self.category == ComponentType.DISK

    @property
    def get_capacity(self):
        # Get the detail capacity of the memory and storage from the name.
        # Input: <size> <unit> <name of the component>
        # Output: <size>, <unit> <name_without_capacity>
        inputs = str(self.name).split(' ')
        size, unit = inputs[0], inputs[1]
        return size, unit

    @property
    def get_true_name(self):
        if self.has_capacity:
            words = self.name.split(" ")
            print(words)
            return " ".join(words[2:]) # Ignore the first 2 words describing capacity
        return self.name


# Laptop
class Laptop(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False, unique=True)
    slug = models.SlugField(max_length=255, null=False, unique=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=7, decimal_places=2, blank=False, null=False)
    link = models.URLField(verbose_name='source', max_length=255, blank=False, null=False)
    updated = models.DateTimeField(auto_now=True)
    specs = models.ManyToManyField(Memo, related_name="specs", through='LaptopNote', through_fields=('laptop', 'memo'))

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


class LaptopNote(models.Model):
    laptop = models.ForeignKey(Laptop, on_delete=models.CASCADE)
    memo = models.ForeignKey(Memo, on_delete=models.CASCADE, related_name="note_detail")
    qnty = models.IntegerField(default=1, help_text="Distinct Component Quantity")

    def __str__(self):
        return "{} is built with {} {}".format(self.laptop, self.qnty, self.memo)