from django.db import models


class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=300, default='')
    price = models.IntegerField(default=0) # cents
    
    def __str_(self):
        return self.name
    
    def get_display_price(self):
        return "{0:.2f}".format(self.price / 100)
    
    
class Order(models.Model):
    
    products = models.CharField(max_length=200)
    quantity = models.CharField(max_length=200)
    
    def __str_(self):
        return self.name
    
    
#class Discount(models.Model):
#    code = models.CharField(max_length=100, default='')
#    percent = models.IntegerField(default=0)
#    
#    def __str_(self):
#        return self.name
