from datetime import datetime as dt

from django.forms import model_to_dict
from orders.models import COURIER_EARNINGS_COEFFICIENTS, Courier, Order
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import (CourierSerializer, OrderAssignmentSerializer,
                          OrderCompletionSerializer, OrderSerializer)
from .service import check_courier_and_orders_compatibility, dict_to_json


@api_view(['POST'])
def api_couriers(request):
    result = []
    serializer = CourierSerializer(data=request.data, many=True)
    if serializer.is_valid():
        serializer.save()
        data = serializer.data
        for i in data:
            result.append({'id': i['courier_id']})
        result = {'couriers': result}
        return Response(dict_to_json(result), status=status.HTTP_201_CREATED)
    result = []
    for i in request.data:
        serializer = CourierSerializer(data=i)
        if serializer.is_valid():
            continue
        result.append({'id': serializer.data.get('courier_id')})
        result[-1].update(serializer.errors)
    result = {'validation_error': {'couriers': result}}
    return Response(dict_to_json(result), status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH', 'GET'])
def api_couriers_detail(request, courier_id):
    courier = Courier.objects.filter(courier_id=courier_id)
    if not courier:
        return Response(dict_to_json({'errors': 'Courier with such id does not exist'}),
                        status=status.HTTP_400_BAD_REQUEST)
    courier = Courier.objects.get(courier_id=courier_id)
    if request.method == 'PATCH':
        serializer = CourierSerializer(courier, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            orders = Order.objects.filter(courier=courier_id)
            suitable_orders = check_courier_and_orders_compatibility(courier_id, courier_id)
            for order in orders:
                if order not in suitable_orders:
                    order.courier = None
                    order.assign_time = None
                    order.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'GET':
        min_time = None
        for region in courier.regions:
            orders = Order.objects.filter(
                courier=courier, region=region
            ).exclude(complete_time=None).order_by('complete_time')
            if not orders:
                continue
            region_time = [(orders[0].complete_time - orders[0].assign_time).total_seconds()]
            previous_order_time = orders[0].complete_time
            for order in orders[1::]:
                time = (order.complete_time - previous_order_time).total_seconds()
                region_time.append(time)
                previous_order_time = order.complete_time
            avg_time = sum(region_time) / len(region_time)
            min_time = avg_time if min_time is None else min(sum(region_time) / len(region_time), min_time)

        rating = None if min_time is None else round((60*60 - min(min_time, 60*60))/(60*60) * 5, 2)

        orders_number = Order.objects.filter(courier=courier).exclude(assign_time=None).count()
        earnings = orders_number * 500 * COURIER_EARNINGS_COEFFICIENTS[courier.courier_type]

        result = model_to_dict(courier)
        result.update({'earnings': earnings})
        if rating is not None:
            result.update({'rating': rating})

        result = dict_to_json(result)
        return Response(result)


@api_view(['POST'])
def api_orders(request):
    result = []
    serializer = OrderSerializer(data=request.data, many=True)
    if serializer.is_valid():
        serializer.save()
        data = serializer.data
        for i in data:
            result.append({'id': i['order_id']})
        result = {'orders': result}
        return Response(dict_to_json(result), status=status.HTTP_201_CREATED)
    result = []
    for i in request.data:
        serializer = OrderSerializer(data=i)
        if serializer.is_valid():
            continue
        result.append({'id': serializer.data.get('order_id')})
        result[-1].update(serializer.errors)
    result = {'validation_error': {'orders': result}}
    return Response(dict_to_json(result), status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def api_orders_assign(request):
    serializer = OrderAssignmentSerializer(data=request.data)
    if serializer.is_valid():
        courier = Courier.objects.get(courier_id=serializer.data.get('courier_id'))
        result = []
        assign_orders = courier.orders.filter(complete_time=None)
        if assign_orders:
            for i in assign_orders:
                result.append({'id': i.order_id})
            date_str = assign_orders[0].assign_time.isoformat('T') + 'Z'
        else:
            suitable_orders = check_courier_and_orders_compatibility(courier.courier_id)
            date_str = dt.now().isoformat('T') + 'Z'
            for i in suitable_orders:
                i.courier = courier
                i.assign_time = date_str
                i.save()
                result.append({'id': i.order_id})
        result = {'orders': result, 'assign_time': date_str} if result else {'orders': result}
        result = dict_to_json(result)
        return Response(result, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def api_orders_complete(request):
    serializer = OrderCompletionSerializer(data=request.data)
    if serializer.is_valid():
        courier = Courier.objects.get(courier_id=serializer.data.get('courier_id'))
        order = Order.objects.get(order_id=serializer.data.get('order_id'), courier=courier)
        order.completed = True
        order.complete_time = dt.strptime(serializer.data.get('complete_time'), "%Y-%m-%dT%H:%M:%S.%fZ")
        order.save()
        result = {'order_id': order.order_id}
        result = dict_to_json(result)
        return Response(result, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
