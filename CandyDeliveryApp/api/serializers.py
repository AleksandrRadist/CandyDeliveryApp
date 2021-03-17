from rest_framework import serializers

from datetime import datetime as dt
from orders.models import Courier, Order
from rest_framework.fields import empty
from rest_framework.settings import api_settings


class CourierSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('courier_id', 'courier_type', 'regions', 'working_hours',)
        model = Courier

    def validate_regions(self, value):
        for i in value:
            if type(i) != type(1) or i <= 0:
                raise serializers.ValidationError('The array must be composed of positive integers')
        return value

    def validate_working_hours(self, value):
        for i in value:
            if not isinstance(i, str):
                raise serializers.ValidationError('The array must be composed of strings')
            try:
                dt.strptime(i[:5:], '%H:%M')
                dt.strptime(i[6::], '%H:%M')

            except ValueError:
                raise serializers.ValidationError('The format of the array elements is incorrect')
        return value

    def run_validation(self, data=empty):
        if data is not empty:
            unknown = set(data) - set(self.fields)
            if unknown:
                errors = ["Unknown field: {}".format(f) for f in unknown]
                raise serializers.ValidationError({
                    api_settings.NON_FIELD_ERRORS_KEY: errors,
                })
        return super(CourierSerializer, self).run_validation(data)


class CourierWithoutIdSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('courier_type', 'working_hours', 'regions',)
        model = Courier

    def validate_regions(self, value):
        for i in value:
            if type(i) != type(1) or i <= 0:
                raise serializers.ValidationError('The array must be composed of positive integers')
        return value

    def validate_working_hours(self, value):
        for i in value:
            if not isinstance(i, str):
                raise serializers.ValidationError('The array must be composed of strings')
            try:
                dt.strptime(i[:5:], '%H:%M')
                dt.strptime(i[6::], '%H:%M')

            except ValueError:
                raise serializers.ValidationError('The format of the array elements is incorrect')
        return value

    def run_validation(self, data=empty):
        if data is not empty:
            unknown = set(data) - set(self.fields)
            if unknown:
                errors = ["Unknown field: {}".format(f) for f in unknown]
                raise serializers.ValidationError({
                    api_settings.NON_FIELD_ERRORS_KEY: errors,
                })
        return super(CourierWithoutIdSerializer, self).run_validation(data)


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('order_id', 'weight', 'region', 'delivery_hours')
        model = Order

    def validate_delivery_hours(self, value):
        for i in value:
            if not isinstance(i, str):
                raise serializers.ValidationError('The array must be composed of strings')
            try:
                dt.strptime(i[:5:], '%H:%M')
                dt.strptime(i[6::], '%H:%M')

            except ValueError:
                raise serializers.ValidationError('The format of the array elements is incorrect')
        return value

    def validate_weight(self, value):
        if value <= 0:
            raise serializers.ValidationError('This field must be positive')
        return value

    def run_validation(self, data=empty):
        if data is not empty:
            unknown = set(data) - set(self.fields)
            if unknown:
                errors = ["Unknown field: {}".format(f) for f in unknown]
                raise serializers.ValidationError({
                    api_settings.NON_FIELD_ERRORS_KEY: errors,
                })
        return super(OrderSerializer, self).run_validation(data)


class OrderAssignmentSerializer(serializers.Serializer):
    courier_id = serializers.IntegerField()

    def validate_courier_id(self, value):
        if value <= 0:
            raise serializers.ValidationError('This field must be positive')
        if Courier.objects.filter(courier_id=value).exists():
            return value
        raise serializers.ValidationError('Courier with such id does not exist')

    def run_validation(self, data=empty):
        if data is not empty:
            unknown = set(data) - set(self.fields)
            if unknown:
                errors = ["Unknown field: {}".format(f) for f in unknown]
                raise serializers.ValidationError({
                    api_settings.NON_FIELD_ERRORS_KEY: errors,
                })
        return super(OrderAssignmentSerializer, self).run_validation(data)


class OrderCompletionSerializer(serializers.Serializer):
    courier_id = serializers.IntegerField()
    order_id = serializers.IntegerField()
    complete_time = serializers.CharField()

    def validate_courier_id(self, value):
        if value <= 0:
            raise serializers.ValidationError('This field must be positive')
        if Courier.objects.filter(courier_id=value).exists():
            return value
        raise serializers.ValidationError('Courier with such id does not exist')

    def validate_order_id(self, value):
        if Order.objects.filter(order_id=value).exists():
            return value
        raise serializers.ValidationError('Order with such id does not exist')

    def validate_complete_time(self, value):
        try:
            dt.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ')

        except ValueError:
            raise serializers.ValidationError('The format is incorrect')
        return value

    def validate(self, data):
        courier = Courier.objects.get(courier_id=data.get('courier_id'))
        if not Order.objects.filter(order_id=data.get('order_id'), courier=courier).exists():
            raise serializers.ValidationError('The order was assigned to another courier or not assigned at all')
        return data

    def run_validation(self, data=empty):
        if data is not empty:
            unknown = set(data) - set(self.fields)
            if unknown:
                errors = ["Unknown field: {}".format(f) for f in unknown]
                raise serializers.ValidationError({
                    api_settings.NON_FIELD_ERRORS_KEY: errors,
                })
        return super(OrderCompletionSerializer, self).run_validation(data)
