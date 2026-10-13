from rest_framework import serializers

from submissions.models import MileageSubmission, MileageSubmissionRow, Role, Submission


class SubmissionRoleSerializer(serializers.ModelSerializer):
    member_ids = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = ["pk", "name", "description", "member_ids"]

    @staticmethod
    def get_member_ids(role):
        return list(role.members.values_list("pk", flat=True))


class MileageSubmissionRowSerializer(serializers.ModelSerializer):
    class Meta:
        model = MileageSubmissionRow
        fields = [
            "pk",
            "row_order",
            "date",
            "purpose",
            "contract_fund",
            "odometer_start",
            "odometer_finish",
            "miles",
        ]
        read_only_fields = ["miles"]


class SubmissionSerializer(serializers.ModelSerializer):
    submitter_pk = serializers.IntegerField(source="submitter.pk", read_only=True)
    submitter_name = serializers.CharField(source="submitter.name", read_only=True)
    approved_by_name = serializers.CharField(
        source="approved_by.name", default="", read_only=True
    )
    mileage_submission_pk = serializers.IntegerField(
        source="mileage_submission.pk", read_only=True
    )
    approver_role_name = serializers.CharField(
        source="approver_role.name", default="", read_only=True
    )

    class Meta:
        model = Submission
        fields = [
            "pk",
            "form_type",
            "status",
            "submitter_pk",
            "submitter_name",
            "approver_role",
            "approver_role_name",
            "approved_by",
            "approved_by_name",
            "submitted_at",
            "approved_at",
            "updated_at",
            "mileage_submission_pk",
        ]


class MileageSubmissionSerializer(serializers.ModelSerializer):
    rows = MileageSubmissionRowSerializer(many=True)
    submitter_pk = serializers.IntegerField(source="submitter.pk", read_only=True)
    submitter_name = serializers.CharField(source="submitter.name", read_only=True)
    total_miles = serializers.IntegerField(read_only=True)
    total_reimbursement = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    submission = serializers.SerializerMethodField()

    class Meta:
        model = MileageSubmission
        fields = [
            "pk",
            "submitter_pk",
            "submitter_name",
            "certification_statement",
            "reimbursement_rate",
            "rows",
            "total_miles",
            "total_reimbursement",
            "created_at",
            "updated_at",
            "submission",
        ]

    @staticmethod
    def get_submission(mileage_submission):
        submission = mileage_submission.submissions.first()
        if not submission:
            return None
        return {
            "pk": submission.pk,
            "status": submission.status,
            "form_type": submission.form_type,
            "approver_role_pk": submission.approver_role.pk
            if submission.approver_role
            else None,
            "approver_role_name": submission.approver_role.name
            if submission.approver_role
            else "",
            "approved_by_name": submission.approved_by.name
            if submission.approved_by
            else "",
            "submitted_at": submission.submitted_at,
            "approved_at": submission.approved_at,
        }

    def create(self, validated_data):
        rows = validated_data.pop("rows", [])
        mileage_submission = MileageSubmission.objects.create(**validated_data)
        for index, row in enumerate(rows):
            MileageSubmissionRow.objects.create(
                mileage_submission=mileage_submission,
                **row,
            )
        return mileage_submission

    def update(self, instance, validated_data):
        rows = validated_data.pop("rows", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if rows is not None:
            instance.rows.all().delete()
            for index, row in enumerate(rows):
                MileageSubmissionRow.objects.create(
                    mileage_submission=instance,
                    row_order=row.get("row_order", index),
                    **row,
                )

        return instance
