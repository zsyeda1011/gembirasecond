from django.db import models

class Store(models.Model):
    id = models.AutoField(primary_key= True)
    title = models.TextField()
   
class Drink(models.Model):
    id = models.AutoField(primary_key= True)
    name = models.TextField()
    store_id = models.ForeignKey(Store,  on_delete=models.CASCADE)
    