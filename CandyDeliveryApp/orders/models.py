from django.core.validators import MinValueValidator
from django.db import models

COURIERS_TYPE_AND_WEIGHT_MAPPING = {
    'foot': 10,
    'bike': 15,
    'car': 50
}

COURIER_EARNINGS_COEFFICIENTS = {
    'foot': 2,
    'bike': 5,
    'car': 10
}


class Courier(models.Model):
    courier_id = models.IntegerField(primary_key=True, validators=[MinValueValidator(1)])
    TYPE_CHOICES = (
        ('foot', 'пеший курьер'),
        ('bike', 'велокурьер'),
        ('car', 'курьер на автомобиле'),
    )
    courier_type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES
    )
    regions = models.JSONField(null=True, blank=True)
    working_hours = models.JSONField(null=True, blank=True)


class Order(models.Model):
    order_id = models.IntegerField(primary_key=True, validators=[MinValueValidator(1)])
    weight = models.FloatField()
    region = models.IntegerField(validators=[MinValueValidator(1)])
    delivery_hours = models.JSONField()
    courier = models.ForeignKey(Courier, null=True, on_delete=models.SET_NULL, blank=True, related_name='orders')
    completed = models.BooleanField(default=False)
    assign_time = models.DateTimeField(null=True, blank=True)
    complete_time = models.DateTimeField(null=True, blank=True)
