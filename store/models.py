from django.db import models
from django.urls import reverse


class Item(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(null=False, blank=True)
    price = models.PositiveIntegerField(null=False, blank=False)
    currency = models.CharField(max_length=3)

    def __str__(self):
        return str(self.name)

    def get_absolute_url(self):
        return reverse('store:buy-item', args=[self.id])


class Order(models.Model):
    items = models.ManyToManyField(Item, related_name='orders')

    def __str__(self):
        return 'order ' + str(self.id)

    # class Tax(models.Model):
#     orders = models.ManyToManyField(Order,related_name='taxes')
#     price = models.PositiveIntegerField()
#     reason = models.TextField()
#     keyword = models.CharField()                  нужно добавить возможность выбирать ключевое слово
#
# class Discount(models.Model):
#     orders = models.ManyToManyField(Order,related_name='discounts')
#     price = models.PositiveIntegerField()
#     reason = models.TextField()
#     keyword = models.CharField()                  нужно добавить возможность выбирать ключевое слово
