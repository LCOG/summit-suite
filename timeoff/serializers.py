from datetime import date
from rest_framework import serializers

from timeoff.models import TimeOffRequest
from people.models import Employee
from people.serializers import EmployeeSerializer


class TimeOffRequestSerializerBase(serializers.HyperlinkedModelSerializer):
    employee_pk = serializers.IntegerField(source='employee.pk')
    employee_name = serializers.CharField(source='employee.name')
    manager_pk = serializers.IntegerField(source='employee.manager.pk')
    conflicts = serializers.ListField(required=False)
    past = serializers.SerializerMethodField()
 
    class Meta:
        model = TimeOffRequest
        fields = [
            'url', 'pk', 'employee_pk', 'employee_name', 'manager_pk',
            'start_date', 'end_date', 'start_time', 'end_time', 'past', 'note',
            'acknowledged', 'created_at', 'acknowledged_at', 'conflicts'
        ]

    @staticmethod
    def get_past(tor):
        # Return true if the request is in the past
        ed = tor.end_date
        if type(ed) == str:
            ed = date.fromisoformat(ed)
        return ed < date.today()


class TimeOffRequestPublicSerializer(TimeOffRequestSerializerBase):
    pass


class TimeOffRequestPrivateSerializer(TimeOffRequestSerializerBase):
    class Meta:
        model = TimeOffRequest
        fields = [
            'url', 'pk', 'employee_pk', 'employee_name', 'manager_pk',
            'start_date', 'end_date', 'start_time', 'end_time', 'past', 'note',
            'private_note', 'acknowledged', 'created_at', 'acknowledged_at',
            'conflicts'
        ]


class ConflictingResponsibilitiesSerializer(EmployeeSerializer):
    responsibility_names = serializers.ListField()

    class Meta:
        model = Employee
        fields = [
            'pk', 'name', 'responsibility_names'
        ]