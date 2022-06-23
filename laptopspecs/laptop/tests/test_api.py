from django.urls import reverse, path, include
from rest_framework import status
from rest_framework.test import APITestCase

class LaptopTest(APITestCase):

    def test_get_single_laptop(self):

        response = self.client.get(reverse('laptop-detail', args={'slug': 'acer-aspire-1'}))
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        response = self.client.get(reverse('laptop-detail', args={'slug': 'nonexisted-slug-name'}))
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)