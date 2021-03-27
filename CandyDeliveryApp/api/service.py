import datetime
import json

from orders.models import COURIERS_TYPE_AND_WEIGHT_MAPPING, Courier, Order


def check_overlap(t1_start, t1_end, t2_start, t2_end):
    return t1_start < t2_end and t1_end > t2_start


def dict_to_json(array):
    r = json.dumps(array)
    return json.loads(r)


def check_courier_and_order_overlap(working_hours, delivery_hours):
    delivery_hours_dt = []
    for i in delivery_hours:
        delivery = i.split('-')
        delivery1 = datetime.datetime.strptime(delivery[0], '%H:%M')
        delivery2 = datetime.datetime.strptime(delivery[1], '%H:%M')
        delivery_hours_dt.append((delivery1, delivery2))
    for i in working_hours:
        work = i.split('-')
        work1 = datetime.datetime.strptime(work[0], '%H:%M')
        work2 = datetime.datetime.strptime(work[1], '%H:%M')
        for j in delivery_hours_dt:
            flag = check_overlap(work1, work2, j[0], j[1])
            if flag:
                return flag
    return False


def check_courier_and_orders_compatibility(courier_id, assigned=None):
    orders = Order.objects.filter(courier=assigned)
    suitable_orders = []
    for order in orders:
        courier = Courier.objects.get(courier_id=courier_id)
        courier_weight = COURIERS_TYPE_AND_WEIGHT_MAPPING[courier.courier_type]
        if order.weight > courier_weight:
            continue
        if order.region not in courier.regions:
            continue
        if not check_courier_and_order_overlap(courier.working_hours, order.delivery_hours):
            continue
        suitable_orders.append(order)
    return suitable_orders
