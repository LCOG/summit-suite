from django.contrib.sites.models import Site

from mainsite.helpers import send_email
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_training_assignment_notification(
        employee, training_name, assignment_pk
    ):
    """
    Send a notification to the employee about the new training assignment.
    """

    current_site = Site.objects.get_current()
    path = f'/phish/training/{assignment_pk}'
    assignment_url = current_site.domain + path
    profile_url = current_site.domain + '/profile'

    subject = f"New Training Assignment: {training_name}"
    html_template = '../templates/email/phish/training-assigned.html'
    html_message = render_to_string(html_template, {
        'training_name': training_name,
        'assignment_url': assignment_url,
        'profile_url': profile_url
    })
    plaintext_message = strip_tags(html_message)
    
    send_email(employee.user.email, subject, plaintext_message, html_message)