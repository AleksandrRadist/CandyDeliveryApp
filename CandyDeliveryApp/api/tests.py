from django.test import Client, TestCase
from django.urls import reverse
import json
from django.utils import timezone as tz
from orders.models import Order, Courier, COURIER_EARNINGS_COEFFICIENTS
from datetime import datetime as dt
import datetime


class TestCouriers(TestCase):
    def setUp(self):
        self.client = Client()
        self.courier = Courier.objects.create(
            courier_id=1, courier_type='bike', regions=[1, 2, 3], working_hours=['11:00-12:00']
        )
        self.order = Order.objects.create(
            order_id=1, weight=14, region=1, delivery_hours=['11:00-13:00'], courier=self.courier, assign_time=dt.now(tz=tz.utc)
        )
        self.orders_number = Order.objects.all().count()

    def test_create_couriers_with_valid_data(self):
        data = [{
            "courier_id": 6,
            "courier_type": "foot",
            "regions": [1, 12, 22],
            "working_hours": ["11:35-14:05", "09:00-11:00"]
            },
            {
            "courier_id": 5,
            "courier_type": "bike",
            "regions": [22],
            "working_hours": ["09:00-18:00"]
            },
            {
            "courier_id": 4,
            "courier_type": "car",
            "regions": [12, 22, 23, 33],
            "working_hours": []
        }]
        response = self.client.post(reverse('couriers'), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Courier.objects.all().count(), self.orders_number + 3)
        self.assertEqual(response.data, {"couriers": [{"id": 6}, {"id": 5}, {"id": 4}]})
        for i in data:
            courier = Courier.objects.get(courier_id=i['courier_id'])
            self.assertEqual(courier.courier_type, i['courier_type'])
            self.assertEqual(courier.regions, i['regions'])
            self.assertEqual(courier.working_hours, i['working_hours'])

    def test_create_couriers_with_invalid_data(self):
        data = [{
                "courier_id": 0,
                "courier_type": "foot",
                "regions": [1, 12, 23],
                "working_hours": ["11:35-14:05", "09:00-11:00"]
                },
                {
                "courier_id": 6,
                "courier_type": "bike",
                "regions": [22],
                "working_hours": ["09:00-18:00", 23]
                },
                {
                "courier_id": 5,
                "courier_type": "bike",
                "regions": ['qwe', 1],
                "working_hours": ["09:00-18:00"]
                },
                {
                "courier_id": 4,
                "courier_type": "feet",
                "regions": [12, 22, 23, 33],
                "working_hours": []
                }]
        response = self.client.post(reverse('couriers'), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Courier.objects.all().count(), self.orders_number)
        self.assertEqual(len(response.data['validation_error']['couriers']), 4)

    def test_patch_couriers(self):
        data = {
            'regions': [2, 3]
        }
        response = self.client.patch(
            reverse('couriers_detail', kwargs={'courier_id': 1}), data=json.dumps(data), content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {
                            "courier_id": 1,
                            "courier_type": "bike",
                            "regions": [2, 3],
                            "working_hours": ["11:00-12:00"]
        })
        courier = Courier.objects.get(courier_id=self.courier.courier_id)
        self.assertEqual(courier.regions, data['regions'])
        order = Order.objects.get(order_id=self.order.order_id)
        self.assertEqual(order.assign_time, None)
        self.assertEqual(order.courier, None)

    def test_get_courier_stats(self):
        Order.objects.create(
            order_id=10, weight=14, region=1, delivery_hours=['11:00-13:00'],
            courier=self.courier, assign_time=dt.now(tz=tz.utc), complete_time=dt.now(tz=tz.utc) + datetime.timedelta(minutes=10)
        )
        response = self.client.get(reverse('couriers_detail', kwargs={'courier_id': self.courier.courier_id}))
        self.assertNotEqual(response.status_code, 404)
        stats = response.data
        print(stats)
        self.assertEqual(stats.get('courier_id'), self.courier.courier_id)
        self.assertEqual(stats.get('courier_type'), self.courier.courier_type)
        self.assertEqual(stats.get('regions'), self.courier.regions)
        self.assertEqual(stats.get('working_hours'), self.courier.working_hours)
        rating = round((60*60 - min(600, 60*60))/(60*60) * 5, 2)
        self.assertEqual(stats.get('rating'), rating)
        earnings = (self.orders_number + 1) * 500 * COURIER_EARNINGS_COEFFICIENTS[self.courier.courier_type]
        self.assertEqual(stats.get('earnings'), earnings)


class TestOrders(TestCase):
    def setUp(self):
        self.client = Client()
        self.courier = Courier.objects.create(
            courier_id=1, courier_type='bike', regions=[1, 2, 3], working_hours=['11:00-12:00']
        )
        self.courier2 = Courier.objects.create(
            courier_id=2, courier_type='bike', regions=[1, 2, 3], working_hours=['11:00-12:00']
        )
        self.order1 = Order.objects.create(
            order_id=10, weight=14, region=1, delivery_hours=['11:00-13:00']
        )
        self.order2 = Order.objects.create(
            order_id=11, weight=14, region=1, delivery_hours=['11:00-13:00']
        )
        Order.objects.create(
            order_id=20, weight=16, region=3, delivery_hours=['11:30-18:00']
        )
        Order.objects.create(
            order_id=30, weight=14, region=30, delivery_hours=['11:30-18:00']
        )
        Order.objects.create(
            order_id=40, weight=14, region=1, delivery_hours=['13:00-14:00']
        )
        self.order3 = Order.objects.create(
            order_id=50, weight=14, region=1, delivery_hours=['11:00-13:00'], courier=self.courier2, assign_time=dt.now(tz=tz.utc)
        )
        self.orders_number = Order.objects.all().count()

    def test_create_orders_with_valid_data(self):
        data = [
            {
                "order_id": 1,
                "weight": 0.11,
                "region": 12,
                "delivery_hours": ["09:00-18:00"]
            },
            {
                "order_id": 2,
                "weight": 15,
                "region": 1,
                "delivery_hours": ["09:00-18:00"]
            },
            {
                "order_id": 3,
                "weight": 1.34,
                "region": 22,
                "delivery_hours": ["09:00-12:00", "16:00-21:30"]
            }
        ]
        response = self.client.post(reverse('orders'), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Order.objects.all().count(), self.orders_number + 3)
        self.assertEqual(response.data, {"orders": [{"id": 1}, {"id": 2}, {"id": 3}]})
        for i in data:
            order = Order.objects.get(order_id=i['order_id'])
            self.assertEqual(order.weight, i['weight'])
            self.assertEqual(order.region, i['region'])
            self.assertEqual(order.delivery_hours, i['delivery_hours'])

    def test_create_orders_with_invalid_data(self):
        data = [
            {
                "order_id": 1,
                "weight": 0.23,
                "region": 12,
                "delivery_hours": ["09:00-18:00"]
            },
            {
                "order_id": 'w',
                "weight": 0.23,
                "region": 12,
                "delivery_hours": ["09:00-18:00"]
            },
            {
                "order_id": 2,
                "weight": -15,
                "region": 1,
                "delivery_hours": ["09:00-18:00"]
            },
            {
                "order_id": 3,
                "weight": 0.01,
                "region": 'q',
                "delivery_hours": ["09:00-12:00", "16:00-21:30"]
            },
            {
                "order_id": 4,
                "weight": -15,
                "region": 1,
                "delivery_hours": ["09:00-18:00", 1]
            },
            {
                "order_id": 'w',
                "weight": 0.23,
                "region": 12,
                "delivery_hours": ["09:00-18:00"],
                'extra': 1
            }
        ]
        response = self.client.post(reverse('orders'), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        print(response.data)
        self.assertEqual(Order.objects.all().count(), self.orders_number)
        self.assertEqual(len(response.data['validation_error']['orders']), 5)

    def test_orders_assign(self):
        data = {'courier_id': self.courier.courier_id}
        response = self.client.post(reverse('orders_assign'), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('orders'), [{'id': self.order1.order_id}, {'id': self.order2.order_id}])
        self.assertEqual(Order.objects.filter(courier_id=self.courier, complete_time=None).count(), 2)
        assign_time = Order.objects.filter(courier_id=self.courier, complete_time=None)[0].assign_time.isoformat('T') + 'Z'
        Order.objects.filter(order_id=self.order1.order_id).update(complete_time=dt.now(tz=tz.utc))
        response = self.client.post(reverse('orders_assign'), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.data, {'orders': [{'id': self.order2.order_id}], 'assign_time': assign_time})

    def test_orders_complete(self):
        data = {
            "courier_id": self.courier2.courier_id,
            "order_id": self.order3.order_id,
            "complete_time": (dt.now() + datetime.timedelta(minutes=10)).isoformat('T') + 'Z'
        }
        response = self.client.post(reverse('orders_complete'), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'order_id': self.order3.order_id})
        self.assertEqual(Order.objects.exclude(complete_time=None).count(), 1)
