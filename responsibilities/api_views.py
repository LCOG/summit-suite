from django.db.models import Q

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from people.models import Employee


from .models import Responsibility, Tag
from .serializers import ResponsibilitySerializer, SimpleTagSerializer, TagSerializer


class ResponsibilityViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Responsibility.objects.all()
    serializer_class = ResponsibilitySerializer

    def get_queryset(self):
        """
        Return a list of all responsibilities for the organization of the
        authenticated user.
        Optionally filter by orphaned responsibilities.
        Optionally filter by employee pk to get primary responsibilities with
        secondaries, or just a list of secondaries.
        """
        user = self.request.user
        if user.is_superuser:
            return Responsibility.objects.all()
        else:
            if user.is_authenticated:
                if not hasattr(user, 'employee'):
                    return Responsibility.objects.none()
                orphaned = self.request.query_params.get('orphaned', None)
                if orphaned is not None and orphaned == "true":
                    queryset = Responsibility.objects.filter(organization=user.employee.organization).filter(
                        Q(primary_employee__isnull=True) | Q(secondary_employee__isnull=True)
                    )
                employee = self.request.query_params.get('employee', None)
                if employee is not None and employee.isdigit():
                    secondary = self.request.query_params.get('secondary', None)
                    if secondary is not None and secondary == 'true':
                        queryset = Responsibility.objects.filter(organization=user.employee.organization, secondary_employee=employee)
                    else:
                        queryset = Responsibility.objects.filter(organization=user.employee.organization, primary_employee=employee)
            else:
                queryset = Responsibility.objects.none()
            return queryset if 'queryset' in locals() else Responsibility.objects.filter(organization=user.employee.organization)

    def create(self, request):
        organization = request.user.employee.organization
        name = request.data['name']
        description = request.data['description'] if 'description' in request.data else ''
        link = request.data['link'] if 'link' in request.data else ''
        tags = request.data['tags'] if 'tags' in request.data else ''
        primary_employee = Employee.objects.get(pk=request.data['primary_employee']) if request.data['primary_employee'] != -1 else None
        secondary_employee = Employee.objects.get(pk=request.data['secondary_employee']) if request.data['secondary_employee'] != -1 else None
        responsibility = Responsibility.objects.create(organization=organization, name=name, description=description, link=link, primary_employee=primary_employee, secondary_employee=secondary_employee)

        tag_objects = []
        for tag in tags:
            tag_object = Tag.objects.get_or_create(
                name=tag['name'], organization=organization
            )
            tag_objects.append(tag_object[0])
        responsibility.tags.set(tag_objects)

        serialized_responsibility = ResponsibilitySerializer(responsibility,
            context={'request': request})
        return Response(serialized_responsibility.data)

    def update(self, request, pk=None):
        organization = request.user.employee.organization
        responsibility = Responsibility.objects.get(pk=pk)
        name = request.data['name']
        description = request.data['description'] if 'description' in request.data else ''
        link = request.data['link'] if 'link' in request.data else ''
        tags = request.data['tags'] if 'tags' in request.data else ''
        primary_employee = Employee.objects.get(pk=request.data['primary_employee']) if request.data['primary_employee'] != -1 else None
        secondary_employee = Employee.objects.get(pk=request.data['secondary_employee']) if request.data['secondary_employee'] != -1 else None
        responsibility.name = name
        responsibility.description = description
        responsibility.link = link
        
        tag_objects = []
        for tag in tags:
            tag_object = Tag.objects.get_or_create(
                name=tag['name'], organization=organization
            )
            tag_objects.append(tag_object[0])
        responsibility.tags.set(tag_objects)

        responsibility.primary_employee = primary_employee
        responsibility.secondary_employee = secondary_employee
        responsibility.save()
        serialized_responsibility = ResponsibilitySerializer(responsibility,
            context={'request': request})
        return Response(serialized_responsibility.data)


class TagViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    def get_queryset(self):
        """
        Return a list of all tags to any authenticated user.
        """
        user = self.request.user
        if user.is_superuser:
            return Tag.objects.all()
        else:
            if user.is_authenticated:
                return Tag.objects.filter(
                    organization=user.employee.organization
                ).order_by('name')
            else:
                return Tag.objects.none()

    # A simple list of employees for populating dropdowns
    @action(detail=False, methods=['get'])
    def simple_list(self, request):
        user = self.request.user
        if user.is_superuser:
            tags = Tag.objects.all()
        else:
            if user.is_authenticated:
                tags = Tag.objects.filter(
                    organization=user.employee.organization
                ).order_by('name')
            else:
                tags = Tag.objects.none()
        serializer = SimpleTagSerializer(tags, many=True)
        return Response(serializer.data)
