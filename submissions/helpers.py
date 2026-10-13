from django.contrib.sites.models import Site

from mainsite.helpers import send_email_multiple
from submissions.models import Submission


def _emails_for_role_members(role):
    if not role:
        return []
    recipients = []
    for member in role.members.select_related("user").all():
        if member.user.email:
            recipients.append(member.user.email)
    return recipients


def send_mileage_submission_created_notification(submission: Submission):
    if submission.form_type != Submission.FORM_TYPE_MILEAGE:
        return 0
    recipients = _emails_for_role_members(submission.approver_role)
    if not recipients:
        return 0
    current_site = Site.objects.get_current()
    url = f"{current_site.domain}/mileage-reimbursement/list"
    subject = f"Mileage reimbursement submitted by {submission.submitter.name}"
    text_body = (
        f"{submission.submitter.name} submitted a mileage reimbursement request.\n"
        f"Review it here: {url}"
    )
    html_body = (
        f"<p>{submission.submitter.name} submitted a mileage reimbursement "
        f"request.</p><p>Review it here: <a href=\"{url}\">{url}</a></p>"
    )
    return send_email_multiple(
        to_addresses=recipients,
        cc_addresses=[],
        subject=subject,
        text_body=text_body,
        html_body=html_body,
    )


def send_mileage_submission_approved_notification(submission: Submission):
    if submission.form_type != Submission.FORM_TYPE_MILEAGE:
        return 0
    if not submission.submitter.user.email:
        return 0
    current_site = Site.objects.get_current()
    url = f"{current_site.domain}/mileage-reimbursement/list"
    subject = "Mileage reimbursement approved"
    text_body = (
        "Your mileage reimbursement request has been approved.\n"
        f"View it here: {url}"
    )
    html_body = (
        "<p>Your mileage reimbursement request has been approved.</p>"
        f"<p>View it here: <a href=\"{url}\">{url}</a></p>"
    )
    return send_email_multiple(
        to_addresses=[submission.submitter.user.email],
        cc_addresses=[],
        subject=subject,
        text_body=text_body,
        html_body=html_body,
    )
