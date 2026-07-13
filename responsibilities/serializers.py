from rest_framework import serializers
from rest_framework.response import Response

from .models import Responsibility, Tag


class SimpleTagSerializer(serializers.HyperlinkedModelSerializer):
    # For use by ResponsibilitySerializer - does not have url or responsibilities
    
    class Meta:
        model = Tag
        fields = ['pk', 'name']


class ResponsibilitySerializer(serializers.HyperlinkedModelSerializer):
    tags = SimpleTagSerializer(many=True)
    organization_pk = serializers.PrimaryKeyRelatedField(
        source='organization', read_only=True
    )
    primary_employee_pk = serializers.SerializerMethodField()
    primary_employee_name = serializers.SerializerMethodField()
    secondary_employee_pk = serializers.SerializerMethodField()
    secondary_employee_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Responsibility
        fields = [
            'url', 'pk', 'organization_pk', 'name', 'description', 'link',
            'tags', 'primary_employee_pk', 'primary_employee_name',
            'secondary_employee_pk', 'secondary_employee_name'
        ]

    @staticmethod
    def get_primary_employee_pk(responsibility):
        if responsibility.primary_employee:
            return responsibility.primary_employee.pk
        else:
            return ''

    @staticmethod
    def get_secondary_employee_pk(responsibility):
        if responsibility.secondary_employee:
            return responsibility.secondary_employee.pk
        else:
            return ''

    @staticmethod
    def get_primary_employee_name(responsibility):
        if responsibility.primary_employee:
            return responsibility.primary_employee.name
        else:
            return ''
    
    @staticmethod
    def get_secondary_employee_name(responsibility):
        if responsibility.secondary_employee:
            return responsibility.secondary_employee.name
        else:
            return ''


class TagSerializer(serializers.HyperlinkedModelSerializer):
    responsibilities = serializers.SerializerMethodField()
    organization_pk = serializers.PrimaryKeyRelatedField(
        source='organization', read_only=True
    )
    
    class Meta:
        model = Tag
        fields = ['url', 'pk', 'organization_pk', 'name', 'responsibilities']

    def get_responsibilities(self, tag):
        responsibilities = tag.responsibility_set.all()
        serializer = ResponsibilitySerializer(
            responsibilities, many=True, context=self.context
        )
        return serializer.data