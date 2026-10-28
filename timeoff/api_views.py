import datetime
from time import time
from responsibilities.models import Responsibility

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from django.contrib.auth.models import Group, User
from django.db.models import Q
from django.shortcuts import get_object_or_404

from mainsite.helpers import is_true_string

from people.models import Employee

from timeoff.helpers import (
    send_employee_manager_acknowledged_timeoff_request_notification,
    send_manager_new_timeoff_request_notification
)
from timeoff.models import TimeOffRequest, TimeOffRequestTemporaryApprover

from timeoff.serializers import (
    ConflictingResponsibilitiesSerializer, TimeOffRequestPrivateSerializer,
    TimeOffRequestPublicSerializer
)


class TimeOffRequestViewSet(viewsets.ModelViewSet):
    queryset = TimeOffRequest.objects.all()
    # permission_classes = [
    #     IsAuthenticatedOrReadOnly
    # ]

    def get_serializer_class(self):
        if 'team' in self.request.GET and is_true_string(self.request.GET['team']):
            return TimeOffRequestPublicSerializer
        else:
            return TimeOffRequestPrivateSerializer

    def get_queryset(self):
        """
        This view should return a list of all time off requests for which
        the currently authenticated user is the manager.
        """
        user = self.request.user
        if user.is_authenticated:
            if user.is_superuser:
                return super().get_queryset()
            elif 'managed' in self.request.GET and is_true_string(self.request.GET['managed']):
                requests = TimeOffRequest.objects.filter(
                    employee__manager=user.employee,
                    # Only get requests that are less than 30 days old
                    end_date__gte=\
                        datetime.date.today() - datetime.timedelta(days=60)
                )
                # If this user is a temporary approver for someone else,
                # also show their requests.
                temporary_approvers = TimeOffRequestTemporaryApprover.objects\
                    .filter(
                        employee_in_stead=user.employee,
                        start_date__lte=datetime.date.today(),
                        end_date__gte=datetime.date.today()
                    )
                for approver in temporary_approvers:
                    employee_on_leave = approver.employee_on_leave
                    employee_requests = TimeOffRequest.objects.filter(
                        employee__manager=employee_on_leave,
                        # Only get requests that are less than 30 days old
                        end_date__gte=\
                            datetime.date.today() - datetime.timedelta(days=60)
                    )
                    requests = requests | employee_requests
            elif 'team' in self.request.GET and is_true_string(self.request.GET['team']):
                # Show requests from everyone including and under your
                # program manager
                program_manager = user.employee.get_program_manager
                program_manager_and_descendants = program_manager\
                    .get_descendants_of_employee(program_manager)
                start = self.request.GET.get('start', None)
                end = self.request.GET.get('end', None)
                if start and end:
                    requests = TimeOffRequest.objects.filter(
                        start_date__gte=start, end_date__lte=end,
                        employee__in=program_manager_and_descendants
                    )
                else:
                    requests = TimeOffRequest.objects.filter(
                        employee__in=program_manager_and_descendants
                    )
            else:
                requests = TimeOffRequest.objects.filter(
                    employee=user.employee
                )
            for request in requests:
                request.conflicts = [
                    {
                        'pk': e.pk,
                        'name': e.name,
                        'responsibility_names': e.responsibility_names
                    } for e in request.conflicting_responsibilities
                ]
            return requests
        else:
            return TimeOffRequest.objects.none()

    def create(self, request):
        if 'from' in request.data['dates']:
            start_date = request.data['dates']['from'].replace('/', '-')
            end_date = request.data['dates']['to'].replace('/', '-')
        else:
            start_date = request.data['dates'].replace('/', '-')
            end_date = request.data['dates'].replace('/', '-')
        start_time = request.data.get('startTime', None)
        end_time = request.data.get('endTime', None)
        note = request.data['note']
        private_note = request.data['privateNote']
        employee = request.user.employee
        timeoffrequest = TimeOffRequest.objects.create(
            start_date=start_date, end_date=end_date, note=note,
            private_note=private_note, start_time=start_time, end_time=end_time,
            employee=employee
        )
        send_manager_new_timeoff_request_notification(timeoffrequest)
        serialized_timeoffrequest = TimeOffRequestPrivateSerializer(
            timeoffrequest, context={'request': request})
        return Response(serialized_timeoffrequest.data)

    def update(self, request, pk=None):
        tor = TimeOffRequest.objects.get(pk=pk)
        if 'from' in request.data['dates']:
            start_date = request.data['dates']['from'].replace('/', '-')
            end_date = request.data['dates']['to'].replace('/', '-')
        else:
            start_date = request.data['dates'].replace('/', '-')
            end_date = request.data['dates'].replace('/', '-')
        tor.start_time = request.data.get('startTime', None)
        tor.end_time = request.data.get('endTime', None)
        tor.note = request.data['note']
        tor.private_note = request.data['privateNote']
        if start_date != str(tor.start_date) or end_date != str(tor.end_date):
            tor.start_date = start_date
            tor.end_date = end_date
            # Reset acknowledged status since we are making a change
            tor.acknowledged = None
        tor.save()
        serialized_tor = TimeOffRequestPrivateSerializer(tor,
            context={'request': request})
        return Response(serialized_tor.data)
    
    def partial_update(self, request, pk=None):
        """
        Acknowledge a time off request.
        """
        tor = TimeOffRequest.objects.get(pk=pk)
        tor.acknowledged = request.data['acknowledged']
        tor.save()
        send_employee_manager_acknowledged_timeoff_request_notification(
            tor, request.user.employee)
        serialized_tor = TimeOffRequestPrivateSerializer(tor,
            context={'request': request})
        return Response(serialized_tor.data)

    # TODO: Duplicated in TimeOffRequest model property
    # TODO: .conflicting_responsibilities. Use a generic helper function to
    # TODO: handle both?
    # A list of employees with time off requests in the same time period with
    # shared/backup responsibilities.
    @action(detail=False, methods=['post'])
    def conflicting_responsibilities(self, request):
        dates = request.data['dates']
        if 'from' in dates:
            start_year, start_month, start_day = dates['from'].split('/')
            end_year, end_month, end_day = dates['to'].split('/')
        else:
            start_year, start_month, start_day = dates.split('/')
            end_year, end_month, end_day = start_year, start_month, start_day
        if 'user' in request.data:
            employee = request.data['user'].employee
        else:
            employee = request.user.employee
        
        # Get all the employees that share a responsibility with this employee
        responsibility_buddies = Employee.objects.filter(
            Q(primary_responsibilities__in=employee.secondary_responsibilities.all()) |
            Q(secondary_responsibilities__in=employee.primary_responsibilities.all())
        ).distinct()

        # Get all the time off requests for those employees that conflict with
        # this request.
        conflicting_tors = TimeOffRequest.objects\
            .filter(employee__in=responsibility_buddies)\
            .exclude(employee=employee)\
            .exclude(
                start_date__gt=datetime.date(int(end_year),
                int(end_month),
                int(end_day))
            )\
            .exclude(
                end_date__lt=datetime.date(int(start_year),
                int(start_month),
                int(start_day))
            )

        # Prune the buddy list of any employees that don't have any conflicting
        # time off requests, and then annotate them with the list of shared
        # responsibilities.
        # First pass: Remove any responsibility buddies that don't have
        # conflicting time off requests.
        for buddy in responsibility_buddies:
            remove_buddy = True
            for tor in conflicting_tors:
                if tor.employee == buddy:
                    remove_buddy = False
            if remove_buddy:
                responsibility_buddies = responsibility_buddies\
                    .exclude(pk=buddy.pk)
        # Second pass: Add the responsibility names to the serialized
        # employees.
        for buddy in responsibility_buddies:
            for tor in conflicting_tors:
                if tor.employee == buddy:
                    conflicting_responsibilities = Responsibility.objects.filter(
                        (Q(primary_employee=employee) & Q(secondary_employee=buddy)) |
                        (Q(secondary_employee=employee) & Q(primary_employee=buddy))
                    )
                    buddy.responsibility_names = [
                        r.name for r in conflicting_responsibilities
                    ]

        serializer = ConflictingResponsibilitiesSerializer(
            responsibility_buddies, many=True, context={'request': request}
        )
        return Response(serializer.data)
