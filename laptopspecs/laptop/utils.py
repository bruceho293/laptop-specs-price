from django.db.models import F

from laptop.models import Laptop, Component, Memo
from laptop.managers import ComponentType

def get_memo_with_component_qnty(laptop: Laptop):
    """
    Get the dictionary of `Memo` objects describling the name of laptop components in the specification.
    
    :param laptop: `Laptop` object.
    :return: a tuple of  `Memo` QuerySet for each component type. 
    """

    memos = Memo.objects.filter(note_detail__laptop=laptop).annotate(qnty=F('note_detail__qnty')).order_by('name')
    cpu = memos.filter(category=ComponentType.CPU)  
    ram = memos.filter(category=ComponentType.RAM)
    gpu = memos.filter(category=ComponentType.GPU)
    disk = memos.filter(category=ComponentType.DISK)

    return cpu, ram, gpu, disk
    

def get_closest_components(laptop: Laptop=None, qnty_memo=None):
    """
    Get the closest matching components based on the specification of the laptop.
    If `qnty_memo` is used, use `qnty_memo` instead.
    
    :param laptop: `Laptop` object.
    :return closest_component: a dict with component type Key and `Component` object Value. 
    """
    cpu, ram, gpu, disk = None, None, None, None

    if qnty_memo is not None:
        cpu, ram, gpu, disk = qnty_memo
    else:
        cpu, ram, gpu, disk = get_memo_with_component_qnty(laptop)
    
    # Get the matching components.
    # Calculate the total price of the components.
    closest_component = {
        'processor': Component.category_manager.get_closest_processor(cpu),
        'memory': Component.category_manager.get_closest_memory_chip(ram),
        'graphics_card': Component.category_manager.get_closest_graphics_card(gpu),
        'storage': Component.category_manager.get_closest_storage(disk) 
    }

    return closest_component

def get_closest_components_price(laptop:Laptop = None, closest_components: dict = None):
    """
    Get the total price of the matching component based on the laptop.
    If both `laptop` and `closest_component` args is supplied, ignore `laptop` and calculate price based on `closest_component`. 
    
    :param laptop: `Laptop` object.
    :param closest_component:  a dict with component type Key and `Component` object Value. 
    :return: the total price of the closest matching components.
    """
    
    if laptop is None and closest_components is None:
        return 0
    elif laptop is not None and closest_components is None:
        closest_components = get_closest_components(laptop)
   
    # If both 'laptop' and 'closest_component' args is supplied,
    # ignore 'laptop' and calculate the total price of 'closest_component' 
    total_comps_price = 0
    for category_comp in closest_components.keys():
        components = closest_components[category_comp]
        if components.exists():
            for component in components:
                count = component.comp_count
                price = component.get_price
                total_comps_price += float(price) * count
    return total_comps_price

def update_price_difference(laptop: Laptop, total_comps_price: int = 0, closest_components: dict = None):
    """
    Update the price difference field that store the price difference
    between the total price of matching components and the laptop price
    in the laptop_laptop database.
    
    :param laptop: `Laptop` object.
    :param total_comps_price: total price of the maching components. 
    :param closest_component: a dict with component type Key and `Component` object Value. 
    :return: the price difference from total price of matching components and laptop price.
    """
    if total_comps_price == 0:
      if closest_components == None: 
        closest_components = get_closest_components(laptop)
      total_comps_price = get_closest_components_price(closest_components=closest_components)
    
    # Update the price difference if it is not equal to the saved price difference.
    price_difference = total_comps_price - float(laptop.get_price)
    if price_difference != laptop.specs_price_difference:
        laptop.specs_price_difference = price_difference
        laptop.save()
    
    return price_difference