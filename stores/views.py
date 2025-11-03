from django.shortcuts import render
from .models import Store, Drink

def cafe(request):
    template_data = {}
    ####create a instance of the store using the store
    store_name, created = Store.objects.get_or_create(id=1, defaults={'title': 'Cafe'})

    ####create a dummy list of drinks with model type drink using the store id that was just created to show that they belong to that store

    dummy_data = [
        {'name': "Latte", "store_id": Store.objects.get(id=1)},
        {'name': "Cappuccino", "store_id": Store.objects.get(id=1)},
        {'name': "Espresso", "store_id": Store.objects.get(id=1)},
        {'name': "Iced Americano", "store_id": Store.objects.get(id=1)},
        {'name': "Caramel Macchiato", "store_id": Store.objects.get(id=1)},
        {'name': "Matcha Latte", "store_id": Store.objects.get(id=1)},
        {'name': "Chai Tea", "store_id": Store.objects.get(id=1)},
        {'name': "Cold Brew", "store_id": Store.objects.get(id=1)},
        {'name': "Mocha", "store_id": Store.objects.get(id=1)},
        {'name': "Strawberry Smoothie", "store_id": Store.objects.get(id=1)},
    ]

    if not Drink.objects.all().exists():
        for drink_dict in dummy_data:
            Drink.objects.create(**drink_dict)

   



    search_term = request.GET.get('search')
    if search_term:
        drinks = Drink.objects.filter(name__icontains=search_term)
    else:
        drinks = Drink.objects.all()

    ###pass the list of drinks into template data so that they can be shown
    template_data["drinks"] = drinks
    template_data["title"] = "Cafe"


    return render(request, 'stores/cafe.html',
                  {'template_data'  :  template_data})
   

