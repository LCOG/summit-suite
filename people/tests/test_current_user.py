from django.contrib.auth.models import User
from django.test import TestCase

from rest_framework.test import APIRequestFactory, force_authenticate

from mainsite.models import Module, Organization
from people.api_views import CurrentUserView
from people.models import Employee
from workflows.models import Role


class CurrentUserSerializerTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.workflow_organization = Organization.objects.create(
            name='Workflow Org'
        )
        Role.objects.create(
            organization=self.workflow_organization,
            name='All Workflows Admins',
            description='All workflow administrators',
        )

    def test_current_user_includes_organization_modules(self):
        organization = Organization.objects.create(name='Road Crew')
        organization.modules.add(
            Module.objects.create(name='timeoff'),
            Module.objects.create(name='responsibilities'),
        )

        user = User.objects.create_user(
            username='alice',
            email='alice@example.com',
            first_name='Alice',
            last_name='Worker',
        )
        Employee.objects.create(user=user, organization=organization)

        request = self.factory.get('/api/v1/current-user/')
        force_authenticate(request, user=user)

        response = CurrentUserView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['organization']['pk'], organization.pk)
        self.assertEqual(response.data['organization']['name'], 'Road Crew')
        self.assertEqual(
            sorted(response.data['organization']['modules']),
            ['responsibilities', 'timeoff']
        )

    def test_current_user_handles_missing_organization(self):
        user = User.objects.create_user(
            username='bob',
            email='bob@example.com',
            first_name='Bob',
            last_name='Worker',
        )
        Employee.objects.create(user=user, organization=None)

        request = self.factory.get('/api/v1/current-user/')
        force_authenticate(request, user=user)

        response = CurrentUserView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.data['organization'])