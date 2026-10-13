from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from rest_framework.test import APIRequestFactory, force_authenticate

from mainsite.models import Organization
from people.models import Employee
from submissions.api_views import MileageSubmissionViewSet
from submissions.models import MileageSubmission, Role, Submission


class MileageSubmissionBackendTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.organization = Organization.objects.create(name="Org")

        self.submitter_user = User.objects.create_user(username="submitter")
        self.submitter = Employee.objects.create(
            user=self.submitter_user,
            organization=self.organization,
            number=3001,
        )

        self.approver_user = User.objects.create_user(username="approver")
        self.approver = Employee.objects.create(
            user=self.approver_user,
            organization=self.organization,
            number=3002,
        )

        self.role = Role.objects.create(
            organization=self.organization,
            name="Mileage Reimbursement Approvers",
            description="Approves mileage reimbursements",
        )
        self.role.members.add(self.approver)

    @patch("submissions.api_views.send_mileage_submission_created_notification")
    def test_submitter_can_create_mileage_submission(self, notify_mock):
        view = MileageSubmissionViewSet.as_view({"post": "create"})
        request = self.factory.post(
            "/api/v1/mileage-submission",
            {
                "rows": [
                    {
                        "date": "2026-10-01",
                        "purpose": "Meeting in Salem",
                        "contract_fund": "Fund A",
                        "odometer_start": 100,
                        "odometer_finish": 150,
                    }
                ]
            },
            format="json",
        )
        force_authenticate(request, user=self.submitter_user)
        response = view(request)

        self.assertEqual(response.status_code, 201)
        mileage_submission = MileageSubmission.objects.get(pk=response.data["pk"])
        submission = mileage_submission.submissions.first()
        self.assertIsNotNone(submission)
        self.assertEqual(submission.status, Submission.STATUS_SUBMITTED)
        self.assertEqual(submission.approver_role, self.role)
        self.assertEqual(mileage_submission.rows.count(), 1)
        self.assertEqual(mileage_submission.rows.first().miles, 50)
        notify_mock.assert_called_once_with(submission)

    @patch("submissions.api_views.send_mileage_submission_approved_notification")
    def test_approver_can_approve(self, notify_mock):
        mileage_submission = MileageSubmission.objects.create(
            organization=self.organization,
            submitter=self.submitter,
        )
        submission = Submission.objects.create(
            organization=self.organization,
            submitter=self.submitter,
            form_type=Submission.FORM_TYPE_MILEAGE,
            status=Submission.STATUS_SUBMITTED,
            approver_role=self.role,
            mileage_submission=mileage_submission,
        )

        view = MileageSubmissionViewSet.as_view({"put": "approve"})
        request = self.factory.put(
            f"/api/v1/mileage-submission/{mileage_submission.pk}/approve",
            {},
            format="json",
        )
        force_authenticate(request, user=self.approver_user)
        response = view(request, pk=mileage_submission.pk)

        self.assertEqual(response.status_code, 200)
        submission.refresh_from_db()
        self.assertEqual(submission.status, Submission.STATUS_APPROVED)
        self.assertEqual(submission.approved_by, self.approver)
        notify_mock.assert_called_once_with(submission)

    def test_submitter_cannot_edit_after_approval(self):
        mileage_submission = MileageSubmission.objects.create(
            organization=self.organization,
            submitter=self.submitter,
        )
        submission = Submission.objects.create(
            organization=self.organization,
            submitter=self.submitter,
            form_type=Submission.FORM_TYPE_MILEAGE,
            status=Submission.STATUS_APPROVED,
            approver_role=self.role,
            approved_by=self.approver,
            approved_at=timezone.now(),
            mileage_submission=mileage_submission,
        )
        view = MileageSubmissionViewSet.as_view({"patch": "partial_update"})
        request = self.factory.patch(
            f"/api/v1/mileage-submission/{mileage_submission.pk}",
            {"certification_statement": "Updated"},
            format="json",
        )
        force_authenticate(request, user=self.submitter_user)
        response = view(request, pk=mileage_submission.pk)

        self.assertEqual(response.status_code, 403)
        submission.refresh_from_db()
        self.assertEqual(submission.status, Submission.STATUS_APPROVED)
