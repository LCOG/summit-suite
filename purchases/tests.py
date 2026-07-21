from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase

from rest_framework.test import APIRequestFactory, force_authenticate

from mainsite.models import Organization
from people.models import Employee
from purchases.api_views import ExpenseGLViewSet, ExpenseMonthViewSet, ExpenseViewSet
from purchases.models import Expense, ExpenseCard, ExpenseGL, ExpenseMonth


class ExpenseReconciliationBackendTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

        self.organization = Organization.objects.create(
            name='Test Organization'
        )
        self.submitter_user = User.objects.create_user(
            username='submitter',
            first_name='Submit',
            last_name='Ter',
        )
        self.submitter = Employee.objects.create(
            user=self.submitter_user,
            organization=self.organization,
            number=1001,
        )

        self.approver_user = User.objects.create_user(
            username='approver',
            first_name='App',
            last_name='Rover',
        )
        self.approver = Employee.objects.create(
            user=self.approver_user,
            organization=self.organization,
            number=1002,
        )

        self.executive_director_user = User.objects.create_user(
            username='executive-director',
            first_name='Exec',
            last_name='Director',
        )
        self.executive_director = Employee.objects.create(
            user=self.executive_director_user,
            organization=self.organization,
            number=1003,
            is_executive_director=True,
        )

        self.card = ExpenseCard.objects.create(
            organization=self.submitter.organization,
            last4='1234',
            assignee=self.submitter,
        )
        self.expense_month = ExpenseMonth.objects.create(
            organization=self.submitter.organization,
            purchaser=self.submitter,
            year=2026,
            month=5,
            card=self.card,
        )
        self.expense = Expense.objects.create(
            organization=self.expense_month.organization,
            month=self.expense_month,
            name='Office chair',
            date=date(2026, 5, 15),
            amount=Decimal('125.00'),
            vendor='Office Supply Co',
        )
        self.gl = ExpenseGL.objects.create(
            expense=self.expense,
            code='6100',
            job='JOB-1',
            activity='ACT-1',
            amount=Decimal('125.00'),
            approver=self.approver,
        )

    def test_submitter_can_submit_an_expense_month(self):
        view = ExpenseMonthViewSet.as_view({'post': 'submit'})
        request = self.factory.post(
            '/api/v1/expense-month/submit/',
            {
                'yearInt': 2026,
                'monthInt': 5,
                'cardPK': self.card.pk,
                'note': 'Submitting for review',
            },
            format='json',
        )
        force_authenticate(request, user=self.submitter_user)

        response = view(request)

        self.assertEqual(response.status_code, 200)
        self.expense_month.refresh_from_db()
        self.expense.refresh_from_db()
        self.assertEqual(self.expense_month.status, ExpenseMonth.STATUS_SUBMITTED)
        self.assertIsNotNone(self.expense_month.submitted_at)
        self.assertEqual(self.expense.status, Expense.STATUS_SUBMITTED)

    def test_approver_can_approve_a_gl(self):
        view = ExpenseGLViewSet.as_view({'put': 'approver_approve'})
        request = self.factory.put(
            f'/api/v1/expense-gl/{self.gl.pk}/approver_approve/',
            {'approve': True},
            format='json',
        )
        force_authenticate(request, user=self.approver_user)

        response = view(request, pk=self.gl.pk)

        self.assertEqual(response.status_code, 200)
        self.gl.refresh_from_db()
        self.expense.refresh_from_db()
        self.expense_month.refresh_from_db()
        self.assertTrue(self.gl.approved)
        self.assertEqual(self.expense.status, Expense.STATUS_APPROVER_APPROVED)
        self.assertEqual(
            self.expense_month.status,
            ExpenseMonth.STATUS_APPROVER_APPROVED,
        )

    def test_submitter_cannot_assign_themself_as_gl_approver(self):
        view = ExpenseViewSet.as_view({'put': 'update'})
        request = self.factory.put(
            f'/api/v1/expense/{self.expense.pk}/',
            {
                'name': self.expense.name,
                'date': '2026-05-15',
                'amount': '125.00',
                'vendor': self.expense.vendor,
                'repeat': False,
                'gls': [
                    {
                        'pk': self.gl.pk,
                        'code': self.gl.code,
                        'job': self.gl.job,
                        'activity': self.gl.activity,
                        'amount': '125.00',
                        'approver': {
                            'pk': self.submitter.pk,
                            'name': self.submitter.name,
                            'legal_name': self.submitter.legal_name,
                            'title': '',
                        },
                    }
                ],
            },
            format='json',
        )
        force_authenticate(request, user=self.submitter_user)

        response = view(request, pk=self.expense.pk)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, 'Approver cannot be the expense submitter.')
        self.gl.refresh_from_db()
        self.assertEqual(self.gl.approver, self.approver)

    def test_executive_director_can_assign_themself_as_gl_approver(self):
        card = ExpenseCard.objects.create(
            organization=self.executive_director.organization,
            last4='4321',
            assignee=self.executive_director,
        )
        expense_month = ExpenseMonth.objects.create(
            organization=self.executive_director.organization,
            purchaser=self.executive_director,
            year=2026,
            month=6,
            card=card,
        )
        expense = Expense.objects.create(
            organization=expense_month.organization,
            month=expense_month,
            name='Executive director meal',
            date=date(2026, 6, 10),
            amount=Decimal('42.00'),
            vendor='Restaurant',
        )
        gl = ExpenseGL.objects.create(
            expense=expense,
            code='6200',
            job='JOB-2',
            activity='ACT-2',
            amount=Decimal('42.00'),
            approver=self.approver,
        )

        view = ExpenseViewSet.as_view({'put': 'update'})
        request = self.factory.put(
            f'/api/v1/expense/{expense.pk}/',
            {
                'name': expense.name,
                'date': '2026-06-10',
                'amount': '42.00',
                'vendor': expense.vendor,
                'repeat': False,
                'gls': [
                    {
                        'pk': gl.pk,
                        'code': gl.code,
                        'job': gl.job,
                        'activity': gl.activity,
                        'amount': '42.00',
                        'approver': {
                            'pk': self.executive_director.pk,
                            'name': self.executive_director.name,
                            'legal_name': self.executive_director.legal_name,
                            'title': '',
                        },
                    }
                ],
            },
            format='json',
        )
        force_authenticate(request, user=self.executive_director_user)

        response = view(request, pk=expense.pk)

        self.assertEqual(response.status_code, 200)
        gl.refresh_from_db()
        self.assertEqual(gl.approver, self.executive_director)
