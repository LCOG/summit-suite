from datetime import datetime, timedelta
from io import StringIO
from django.apps import apps
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.utils import timezone

from mainsite.helpers import MANAGER_SIGNATURE_REMINDER, send_email_multiple
from people.models import PerformanceReview


def send_manager_pr_notices():
    # Notification #0
    now = timezone.now()
    one_year_from_now = now + timedelta(days=365)
    upcoming_reviews = PerformanceReview.objects.filter(
        period_end_date__lte=one_year_from_now,
        period_end_date__gte=now,
        employee__active=True
    ).exclude(
        status=PerformanceReview.EVALUATION_HR_PROCESSED,
    ).select_related(
        'employee',
        'employee__manager',
        'employee__manager__user',
        'employee__manager__manager',
        'employee__manager__manager__user',
    ).order_by('employee__manager_id', 'period_end_date', 'pk')

    # CC 'PR Completed Employees' group on all emails
    cc_emails = list(
        Group.objects.get(name='PR Completed Employees')
        .user_set.exclude(email='')
        .values_list('email', flat=True)
    )

    current_site = Site.objects.get_current()
    url = current_site.domain + '/reviews/dashboard'

    def send_manager_email(manager, body_lines, html_items):
        body = StringIO()
        html_body = StringIO()

        body.write(f'Below is a list of your team\'s next review dates. See all here: {url}\n\n')
        html_body.write(
            f'<p>Below is a list of your team\'s next review dates. See all here: '
            f'<a href="{url}">{url}</a></p><ul>'
        )

        body.write(''.join(body_lines))
        html_body.write(''.join(html_items))
        html_body.write('</ul>')

        # Add a note that recent changes may not be reflected in the data
        body.write('\nPlease note that recent changes may not yet be reflected in the data.')
        html_body.write('<p>Please note that recent changes may not yet be reflected in the data.</p>')
        # Add a note to email me if there are any errors with the review data
        body.write('\nIf you notice any errors, please send an email to webupdates@lcog-or.gov.')
        html_body.write(
            '<p>If you notice any errors, please send an email to '
            '<a href="mailto:webupdates@lcog-or.gov">webupdates@lcog-or.gov</a>.</p>'
        )

        if manager.manager is not None and not manager.manager.is_executive_director:
            cc_list = cc_emails + [manager.manager.user.email]
        else:
            cc_list = cc_emails

        send_email_multiple(
            [manager.user.email],
            cc_list,
            'Next Review Dates',
            body.getvalue(),
            html_body.getvalue()
        )

    count = 0
    current_manager_id = None
    current_manager = None
    body_lines = []
    html_items = []

    for review in upcoming_reviews.iterator(chunk_size=500):
        manager = review.employee.manager
        if manager is None:
            continue

        if current_manager_id is None:
            current_manager_id = manager.pk
            current_manager = manager

        if manager.pk != current_manager_id:
            send_manager_email(current_manager, body_lines, html_items)
            count += 1

            current_manager_id = manager.pk
            current_manager = manager
            body_lines = []
            html_items = []

        if review.evaluation_type == PerformanceReview.PROBATIONARY_EVALUATION:
            suffix = ' (Probationary)'
        else:
            suffix = ''

        body_lines.append(
            f'- {review.employee.name}: {review.period_end_date.strftime("%m/%d/%Y")}{suffix}\n'
        )
        html_items.append(
            f'<li>{review.employee.name}: {review.period_end_date.strftime("%m/%d/%Y")}{suffix}</li>'
        )

    if current_manager is not None:
        send_manager_email(current_manager, body_lines, html_items)
        count += 1

    return count


def send_pr_signature_reminders():
    # Notification #11
    SignatureReminder = apps.get_model('people.SignatureReminder')
    current_site = Site.objects.get_current()
    unsigned_reminders = SignatureReminder.objects.filter(
        signed=False, next_date__lte=timezone.now()
    )
    count = 0
    for reminder in unsigned_reminders:
        review = reminder.review
        manager = reminder.employee
        url = current_site.domain + '/pr/' + str(review.pk)
        send_email_multiple(
            [manager.user.email],
            [],
            f'Follow-Up Reminder: Signature required for {review.employee.name}\'s performance review',
            f'{review.employee.manager.name} has completed an evaluation for {review.employee.name}, which requires your signature. View and sign here: {url}',
            f'{review.employee.manager.name} has completed an evaluation for {review.employee.name}, which requires your signature. View and sign here: <a href="{url}">{url}</a>'
        )
        reminder.next_date = datetime.today() + timedelta(days=MANAGER_SIGNATURE_REMINDER)
        reminder.save()
        count += 1
    return count
