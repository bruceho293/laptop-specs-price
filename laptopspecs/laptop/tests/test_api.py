from django.urls import reverse, path, include
from rest_framework import status
from rest_framework.test import APITestCase

from laptop.models import Brand, Memo, LaptopNote, Laptop, Component

class LaptopAPITestCase(APITestCase):
    def setUp(self):
        brand = Brand.objects.create(name="Brand", link="url.com")

        laptop = Laptop.objects.create(name="Sample Laptop", slug="sample-laptop", brand=brand, price=10, link="laptopurl.com")
        cpu = Memo.objects.create(name="Latest Processor 1", category='CPU')
        ram = Memo.objects.create(name="8 GB Advanced Memory Expert 1", category='RAM')
        gpu = Memo.objects.create(name="Graphics Card LD 2", category='GPU')
        disk = Memo.objects.create(name="256 GB Large Storage 1", category='DISK')

        LaptopNote.objects.create(laptop=laptop, memo=cpu)
        LaptopNote.objects.create(laptop=laptop, memo=ram)
        LaptopNote.objects.create(laptop=laptop, memo=gpu)
        LaptopNote.objects.create(laptop=laptop, memo=disk)

        Component.objects.create(name="Latest Processor Expert 1", category='CPU', price=1.1, brand=brand, link="Link 1")
        Component.objects.create(name="16 GB Advanced Expert 2", category='RAM', price=1.1, brand=brand, link="Link 9")
        Component.objects.create(name="Graphics Card LD 2", category='GPU', price=1.1, brand=brand, link="Link 10")
        Component.objects.create(name="256 GB Extra Large Storage 1", category='DISK', price=1.1, brand=brand, link="Link 10")

    # Retrieve the detail of a single laptop.    
    def test_get_single_laptop(self):
        response = self.client.get(reverse('laptop-detail', kwargs={'slug': 'sample-laptop'}))
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        response = self.client.get(reverse('laptop-detail', kwargs={'slug': 'nonexisted-slug-name'}))
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)

    # Retrieve the information about the matching components.
    def test_get_matching_laptop(self):
        response = self.client.get(reverse('laptop-get-matching-components', kwargs={'slug': 'sample-laptop'}))
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertEquals(len(data), 3, "There should be only 3 matching components returning.")