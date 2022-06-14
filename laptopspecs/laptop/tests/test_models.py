from django.test import TestCase
from django.db.models import F
from datetime import datetime

from laptop.models import Brand, Component, Laptop, Memo, LaptopNote


class ComponentTest(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        cls.brand_1 = Brand.objects.create(name="HP")
        cls.brand_2 = Brand.objects.create(name="Brand 2")
        cls.cpu_1 = Component.objects.create(name="Latest Tech Processor 1", category='CPU', price=5.1, brand=cls.brand_1, link="Link 1")
        cls.gpu_1 = Component.objects.create(name="Graphics Card 1", category='GPU', price=4.5, brand=cls.brand_2, link="Link 2")
        cls.gpu_2 = Component.objects.create(name="Graphics Card LD GX 2", category='GPU', price=5.5, brand=cls.brand_2, link="Link 3")
        cls.ram_1 = Component.objects.create(name="8 GB Advanced Memory Load Expert 1", category='RAM', price=3.5, brand=cls.brand_2, link="Link 4")
        cls.disk_1 = Component.objects.create(name="256 GB SSD Large Storage 1", category='DISK', price=2.5, brand=cls.brand_2, link="Link 5")
        cls.laptop = Laptop.objects.create(
            name="HP laptop",
            brand=cls.brand_1,
            price=10.5,
            link="Source Link",
        )
        cpu = Memo.objects.create(name="Latest Processor 1", category='CPU')
        ram = Memo.objects.create(name="8 GB Advanced Memory Expert 1", category='RAM')
        gpu = Memo.objects.create(name="Graphics Card LD 2", category='GPU')
        disk = Memo.objects.create(name="256 GB Large Storage 1", category='DISK')

        LaptopNote.objects.create(laptop=cls.laptop, memo=cpu)
        LaptopNote.objects.create(laptop=cls.laptop, memo=ram)
        LaptopNote.objects.create(laptop=cls.laptop, memo=gpu)
        LaptopNote.objects.create(laptop=cls.laptop, memo=disk)

        Component.objects.create(name="Processor 0", category='CPU', price=1.1, brand=cls.brand_1, link="Link 1")
        Component.objects.create(name="8 GB Memory 0", category='RAM', price=1.1, brand=cls.brand_1, link="Link 9")
        Component.objects.create(name="256 GB Storage 0", category='DISK', price=1.1, brand=cls.brand_1, link="Link 10")

    def test_retrieve_component_based_on_category(self):
        '''
            Check if we can retrieve components belong to a specific category.
        '''
        cpus = Component.category_manager.get_processors()
        gpus = Component.category_manager.get_graphics_cards()
        rams = Component.category_manager.get_memory_chips()
        storages = Component.category_manager.get_storages()

        self.assertEquals(len(cpus), 2, "Incorrect quantity of CPU components.")
        self.assertEquals(len(gpus), 2, "Incorrect quantity of GPU components.")
        self.assertEquals(len(rams), 2, "Incorrect quantity of RAM components.")
        self.assertEquals(len(storages), 2, "Incorrect quantity of DISK components.")

        self.assertTrue(self.cpu_1 in cpus, "{} should be in CPU component queryset.".format(self.cpu_1))
        self.assertFalse(self.gpu_1 in cpus, "{} should not be in CPU component queryset.".format(self.gpu_1))
        self.assertTrue(self.gpu_2 in gpus, "{} should be in GPU component queryset.".format(self.gpu_2))

    def test_retrieve_component_from_laptop(self):
        '''
            Given a laptop along with the name of components, retrieve the accoding components
        '''
        memos = Memo.objects.filter(note_detail__laptop=self.laptop).annotate(qnty=F('note_detail__qnty')).order_by('name')


        laptop_cpu = memos.filter(category='CPU')
        laptop_gpu = memos.filter(category='GPU')
        laptop_ram = memos.filter(category='RAM')
        laptop_disk = memos.filter(category='DISK')

        self.assertEquals(
            self.cpu_1, 
            Component.category_manager.get_closest_processor(laptop_cpu)[0],
            '{} should be in {}'.format(self.cpu_1, laptop_cpu)
            )
        self.assertNotEquals(
            self.gpu_1, 
            Component.category_manager.get_closest_graphics_card(laptop_gpu)[0],
            "{} should not be in {}".format(self.gpu_1, laptop_gpu)
            )
        self.assertEquals(
            self.gpu_2, 
            Component.category_manager.get_closest_graphics_card(laptop_gpu)[0],
            "{} should be in {}".format(self.gpu_2, laptop_gpu)
            )
        self.assertEquals(
            self.ram_1, 
            Component.category_manager.get_closest_memory_chip(laptop_ram)[0],
            "{} should be in {}".format(self.ram_1, laptop_ram)
            )
        self.assertEquals(
            self.disk_1, 
            Component.category_manager.get_closest_storage(laptop_disk)[0],
            "{} should be in {}".format(self.disk_1, laptop_disk))