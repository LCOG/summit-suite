from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from submissions.helpers import (
    send_mileage_submission_approved_notification,
    send_mileage_submission_created_notification,
)
from submissions.models import MileageSubmission, Role, Submission
from submissions.serializers import (
    MileageSubmissionSerializer,
    SubmissionRoleSerializer,
    SubmissionSerializer,
)


DEFAULT_MILEAGE_APPROVER_ROLE_NAME = "Mileage Reimbursement Approvers"


def get_default_mileage_approver_role(employee):
    return Role.objects.filter(
        organization=employee.organization,
        name=DEFAULT_MILEAGE_APPROVER_ROLE_NAME,
    ).first()


def can_approve_submission(employee, submission):
    if not employee:
        return False
    if submission.approver_role:
        return submission.approver_role.members.filter(pk=employee.pk).exists()
    return False


class SubmissionRoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = SubmissionRoleSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            if user.is_superuser:
                return Role.objects.all()
            if hasattr(user, "employee"):
                return Role.objects.filter(organization=user.employee.organization)
        return Role.objects.none()

    def create(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)


class SubmissionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Submission.objects.all().select_related(
        "submitter", "approver_role", "approved_by", "mileage_submission"
    )
    serializer_class = SubmissionSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            if user.is_superuser:
                return self.queryset
            if hasattr(user, "employee"):
                employee = user.employee
                organization_submissions = Submission.objects.filter(
                    organization=employee.organization
                ).select_related(
                    "submitter",
                    "approver_role",
                    "approved_by",
                    "mileage_submission",
                )
                if Role.objects.filter(
                    organization=employee.organization, members=employee
                ).exists():
                    return organization_submissions
                return organization_submissions.filter(submitter=employee)
        return Submission.objects.none()


class MileageSubmissionViewSet(viewsets.ModelViewSet):
    queryset = MileageSubmission.objects.all().prefetch_related("rows", "submissions")
    serializer_class = MileageSubmissionSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            if user.is_superuser:
                return self.queryset
            if hasattr(user, "employee"):
                employee = user.employee
                submissions = Submission.objects.filter(
                    organization=employee.organization,
                    form_type=Submission.FORM_TYPE_MILEAGE,
                ).select_related("submitter", "approver_role")
                if Role.objects.filter(
                    organization=employee.organization, members=employee
                ).exists():
                    mileage_pks = submissions.values_list("mileage_submission_id", flat=True)
                else:
                    mileage_pks = submissions.filter(
                        submitter=employee
                    ).values_list("mileage_submission_id", flat=True)
                return MileageSubmission.objects.filter(pk__in=mileage_pks).prefetch_related(
                    "rows", "submissions__approver_role", "submissions__approved_by"
                )
        return MileageSubmission.objects.none()

    def create(self, request, *args, **kwargs):
        if not hasattr(request.user, "employee"):
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mileage_submission = serializer.save(
            organization=request.user.employee.organization,
            submitter=request.user.employee,
        )
        approver_role = None
        approver_role_pk = request.data.get("approver_role_pk")
        if approver_role_pk:
            approver_role = Role.objects.filter(
                pk=approver_role_pk,
                organization=request.user.employee.organization,
            ).first()
        if not approver_role:
            approver_role = get_default_mileage_approver_role(request.user.employee)
        submission = Submission.objects.create(
            organization=request.user.employee.organization,
            submitter=request.user.employee,
            form_type=Submission.FORM_TYPE_MILEAGE,
            status=Submission.STATUS_SUBMITTED,
            approver_role=approver_role,
            mileage_submission=mileage_submission,
        )
        send_mileage_submission_created_notification(submission)
        output = self.get_serializer(mileage_submission)
        return Response(output.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        submission = instance.submissions.first()
        if not submission:
            return Response(
                data="Submission record is missing for this mileage submission.",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        if not submission.can_edit(getattr(request.user, "employee", None)):
            return Response(
                data="Only the submitter can edit before approval.",
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        submission = instance.submissions.first()
        if not submission:
            return Response(
                data="Submission record is missing for this mileage submission.",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        if not submission.can_edit(getattr(request.user, "employee", None)):
            return Response(
                data="Only the submitter can edit before approval.",
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().partial_update(request, *args, **kwargs)

    @action(detail=True, methods=["put"])
    def approve(self, request, pk=None):
        if not hasattr(request.user, "employee"):
            return Response(status=status.HTTP_403_FORBIDDEN)
        mileage_submission = self.get_object()
        submission = mileage_submission.submissions.first()
        if not submission:
            return Response(
                data="Submission record is missing for this mileage submission.",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        if submission.status == Submission.STATUS_APPROVED:
            return Response(
                data="Submission is already approved.",
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not can_approve_submission(request.user.employee, submission):
            return Response(
                data="You do not have approval permissions for this submission.",
                status=status.HTTP_403_FORBIDDEN,
            )
        submission.approve(request.user.employee)
        send_mileage_submission_approved_notification(submission)
        serialized = self.get_serializer(mileage_submission)
        return Response(serialized.data)
