import csv

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from mainsite.models import Organization
from people.models import Division, Employee, JobTitle, UnitOrProgram


class Command(BaseCommand):
    help = 'Imports employees after exporting from Caselle'

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str)

    def get_title(self, title):
        new_title = title
        if title in ['Senior Financial Analyst']:
            new_title = 'Senior Financial Analyst (Government Services)'
        elif title in ['IS Data Center & Systems Manager']:
            new_title = 'Data Center and Systems Manager'
        elif title in ['GIS Senior Analyst']:
            new_title = 'GIS Senior'
        elif title in ['IS Assistant']:
            new_title = 'IS Assistant (Help Desk)'
        elif title in ['Safe Routes to School Coord.']:
            new_title = 'Safe Routes to School Coordinator'
        elif title in ['Adult Protective Servs. Specialist']:
            new_title = 'APS Specialist'
        elif title in ['APS Lead Specialist']:
            new_title = 'APS Specialist Lead Worker'
        elif title in ['Case Manager.']:
            new_title = 'Case Manager'
        elif title in ['Case Manager - Housing Navigator Focus']:
            new_title = 'Case Manager: Housing Navigator Focus'
        elif title in ['Diversion/ Transition']:
            new_title = 'Diversion/Transition Case Manager'
        elif title in ['Health Promotion Disease Prevention Program Coord.']:
            new_title = 'Disease Prevention & Health Promotion Program Coordinator'
        elif title in ['Senior and Disability Services Director']:
            new_title = 'Division Director'
        elif title in ['HCW Specialist']:
            new_title = 'Home Care Worker Specialist'
        elif title in ['Licensing & Monitoring Assistant']:
            new_title = 'Licensing and Monitoring Assistant'
        elif title in ['Licensing & Monitoring Specialist']:
            new_title = 'Licensing and Monitoring Specialist'
        elif title in ['Pre Admission Screener']:
            new_title = 'Pre-Admission Screener'
        elif title in ['Senior Meals Kitchen Assistant']:
            new_title = 'Senior Meals - Kitchen Assistant'
        elif title in ['Senior Meals Site Coordinator']:
            new_title = 'Senior Meals - Site Coordinator'
        elif title in ['Senior Meals Lead']:
            new_title = 'Senior Meals Lead Worker'
        elif title in ['TAD / Case Manager']:
            new_title = 'Transition and Diversion Case Manager'
        return new_title

    def handle(self, *args, **options):
        # Set up database if new
        lcog = Organization.objects.get(name='LCOG')
        if not Division.objects.filter(name='Administrative Services').count():
            d = Division.objects.create(name='Administrative Services', organization=lcog)
            UnitOrProgram.objects.create(name='-', division=d)
            UnitOrProgram.objects.create(name='Administration', division=d)
        if not Division.objects.filter(name='Government Services').count():
            d = Division.objects.create(name='Government Services', organization=lcog)
            UnitOrProgram.objects.create(name='-', division=d)
            UnitOrProgram.objects.create(name='Business Services', division=d)
            UnitOrProgram.objects.create(name='GIS', division=d)
            UnitOrProgram.objects.create(name='Information Services', division=d)
            UnitOrProgram.objects.create(name='MetroTV Services', division=d)
            UnitOrProgram.objects.create(name='Planning Services', division=d)
            UnitOrProgram.objects.create(name='Technology Services', division=d)
            UnitOrProgram.objects.create(name='Telecom', division=d)
            UnitOrProgram.objects.create(name='Transport Services', division=d)
        if not Division.objects.filter(name='Senior & Disability Services').count():
            d = Division.objects.create(name='Senior & Disability Services', organization=lcog)
            UnitOrProgram.objects.create(name='-', division=d)
            UnitOrProgram.objects.create(name='Area Plan', division=d)
            UnitOrProgram.objects.create(name='Senior Meals', division=d)
        if not Division.objects.filter(name='Test Division').count():
            d = Division.objects.create(name='Test Division', organization=lcog)
            UnitOrProgram.objects.create(name='-', division=d)
            UnitOrProgram.objects.create(name='Test Unit', division=d)
        
        # Import from file
        path = options['path']
        if not path:
            path = 'people/management/employees.csv'
        
        # Keep track of all employee numbers to deactivate removed employees
        numbers_in_file = []

        dataReader = csv.reader(open(path), delimiter=',', quotechar='"')
        for row in dataReader:
            # Parse row data
            number = row[0]
            last_name = row[1]
            first_name = row[2]
            email = row[3].lower()

            if not email:
                self.stdout.write("vvvvvvvvvvvv WARNING vvvvvvvvvvv")
                self.stdout.write(
                    'No email for employee {} {}'.format(first_name, last_name)
                )
                self.stdout.write("^^^^^^^^^^^^ WARNING ^^^^^^^^^^^^")
                username = first_name[0].lower() + last_name.lower()
            else:
                username = email
            
            numbers_in_file.append(int(number))
            
            title = row[4]
            job_title, created = JobTitle.objects.get_or_create(
                name=self.get_title(title),
                organization=Organization.objects.get(name='LCOG')
            )
            if created:
                self.stdout.write("vvvvvvvvvvvv WARNING vvvvvvvvvvv")
                self.stdout.write(
                    'Created job title {} for employee {} {}'.format(
                        job_title, first_name, last_name
                    )
                )
                self.stdout.write("^^^^^^^^^^^^ WARNING ^^^^^^^^^^^^")
            
            department = row[6]
            if department in ['Administration', 'Admin Wilson']:
                unit_or_program = UnitOrProgram.objects.get(name='Administration')
            elif department in ['ADRC']:
                unit_or_program = UnitOrProgram.objects.get(name='ADRC')
            elif department in ['APS1', 'APS2', 'APS3', 'APS4']:
                unit_or_program = UnitOrProgram.objects.get(name='APS')
            elif department in ['Case Management 1', 'Case Management 2', 'Case Management 3', 'Case Management 4', 'Case Management 5', 'Case Management 6']:
                unit_or_program = UnitOrProgram.objects.get(name='Case Management')
            elif department in ['Cottage Grove']:
                unit_or_program = UnitOrProgram.objects.get(name='Cottage Grove')
            elif department in ['Development']:
                unit_or_program = UnitOrProgram.objects.get(name='Development')
            elif department in ['DPG']:
                unit_or_program = UnitOrProgram.objects.get(name='DPG')
            elif department in ['Eligibility1', 'Eligibility 2', 'Eligibility 3']:
                unit_or_program = UnitOrProgram.objects.get(name='Eligibility')
            elif department in ['Facilities']:
                unit_or_program = UnitOrProgram.objects.get(name='Facilities')
            elif department in ['Finance & Budget', 'Finance & Budget 2']:
                unit_or_program = UnitOrProgram.objects.get(name='Finance & Budget')
            elif department in ['Florence']:
                unit_or_program = UnitOrProgram.objects.get(name='Florence')
            elif department in ['GIS']:
                unit_or_program = UnitOrProgram.objects.get(name='GIS')
            elif department in ['Human Resources', 'Human Resources 2']:
                unit_or_program = UnitOrProgram.objects.get(name='Human Resources')
            elif department in ['Information Services', 'Information Services 2', 'Information Services 3']:
                unit_or_program = UnitOrProgram.objects.get(name='Information Services')
            elif department in ['Leads']:
                unit_or_program = UnitOrProgram.objects.get(name='Leads')
            elif department in ['LGPS']:
                unit_or_program = UnitOrProgram.objects.get(name='LGPS')
            elif department in ['Metro TV']:
                unit_or_program = UnitOrProgram.objects.get(name='Metro TV')
            elif department in ['Minutes Recorder']:
                unit_or_program = UnitOrProgram.objects.get(name='Minutes Recorder')
            elif department in ['Planning']:
                unit_or_program = UnitOrProgram.objects.get(name='Planning')
            elif department in ['Program Management']:
                unit_or_program = UnitOrProgram.objects.get(name='Program Management')
            elif department in ['Senior Connections 1', 'Senior Connections 2']:
                unit_or_program = UnitOrProgram.objects.get(name='Senior Connections')
            elif department in ['Senior Meals']:
                unit_or_program = UnitOrProgram.objects.get(name='Senior Meals')
            elif department in ['Support 1', 'Support 2', 'Support 3']:
                unit_or_program = UnitOrProgram.objects.get(name='Support')
            elif department in ['Transportation']:
                unit_or_program = UnitOrProgram.objects.get(name='Transportation')
            elif department in ['Unit Managers 1', 'Unit Managers 2', 'Unit Managers 3', 'Unit Managers 4']:
                unit_or_program = UnitOrProgram.objects.get(name='Unit Managers')
            else:
                raise ValueError('Unknown department {}'.format(department))

            # Get or create user by employee number. Update user names if necessary.
            try:
                user = User.objects.get(employee__number=number)
                if user.first_name != first_name or user.last_name != last_name:
                    user.first_name = first_name
                    user.last_name = last_name
                    user.save()
                    self.stdout.write(
                        'Updated user {} {} name'.format(user.first_name, user.last_name)
                    )
                
                # TEMP: Keep @lcog-or.gov emails until Caselle is updated
                if user.email.endswith('@lcog-or.gov'):
                    username = user.email

                if user.username != username:
                    user.username = username
                    user.save()
                    self.stdout.write(
                        'Updated user {} {} username to {}'.format(user.first_name, user.last_name, user.username)
                    )
                if user.email != email:
                    # Don't update email if we're just updating from @lcog-or.gov to @lcog.org
                    if user.email.endswith('@lcog-or.gov') and email.endswith('@lcog.org'):
                        pass
                        # self.stdout.write(
                        #     'Skipping email update for user {} {} from {} to {}'
                        #         .format(user.first_name, user.last_name, user.email, email)
                        # )
                    else:
                        user.email = email
                        user.save()
                        self.stdout.write(
                            'Updated user {} {} email to {}'.format(user.first_name, user.last_name, user.email)
                        )
            except User.DoesNotExist:
                try:
                    user = User.objects.create(email=email, username=username, first_name=first_name, last_name=last_name)
                except Exception as e:
                    self.stdout.write("vvvvvvvvvvvv EXCEPTION vvvvvvvvvvv")
                    self.stdout.write(
                        'Error creating user {} {}: {}'.format(first_name, last_name, str(e))
                    )
                    self.stdout.write("^^^^^^^^^^^^ EXCEPTION ^^^^^^^^^^^^")
                    continue
                self.stdout.write(
                    'Created user {} {}'.format(user.first_name, user.last_name)
                )
                
            # Get or create employee. Activate them if they are a returning
            # employee. Update employee title and department if necessary.
            try:
                employee = Employee.objects.get(user=user)
                if not employee.active:
                    employee.active = True
                    employee.save()
                    self.stdout.write(
                        'Reactivated returning employee {} {}'.format(employee.user.first_name, employee.user.last_name)
                    )
                updated_title = employee.job_title != job_title
                updated_department = employee.unit_or_program != unit_or_program
                if updated_title or updated_department:
                    if updated_title:
                        old_title = employee.job_title
                        employee.job_title = job_title
                        employee.save()
                        self.stdout.write(
                            'Updated employee {} {} title from {} to {}'
                                .format(
                                    employee.user.first_name,
                                    employee.user.last_name,
                                    old_title,
                                    job_title
                                )
                        )
                    if updated_department:
                        old_department = employee.unit_or_program
                        employee.unit_or_program = unit_or_program
                        employee.save()
                        self.stdout.write(
                            'Updated employee {} {} department from {} to {}'.format(employee.user.first_name, employee.user.last_name, old_department, unit_or_program)
                        )
            except Employee.DoesNotExist:
                lcog_org = Organization.objects.get(name='LCOG')
                employee = Employee.objects.create(
                    user=user, number=number, job_title=job_title,
                    unit_or_program=unit_or_program, organization=lcog_org
                )
                self.stdout.write(
                    'Created employee {} {}'.format(employee.user.first_name, employee.user.last_name)
                )

        # Deactivate any employee not in the list
        for employee in Employee.active_objects.filter(organization__name='LCOG'):
            if employee.number not in numbers_in_file and not employee.temporary:
                employee.active = False
                employee.save()
                self.stdout.write(
                    'Deactivated employee {} {}'.format(employee.user.first_name, employee.user.last_name)
                )

        # Add managers
        dataReader = csv.reader(open(path), delimiter=',', quotechar='"')
        for row in dataReader:
            number = row[0]
            user = User.objects.get(employee__number=number)
            employee = Employee.objects.get(user=user)
            manager_number = row[7]
            manager = None
            if manager_number:
                try:
                    manager = Employee.objects.get(user__employee__number=manager_number)
                except Employee.DoesNotExist:
                    self.stdout.write("vvvvvvvvvvvv WARNING vvvvvvvvvvv")
                    self.stdout.write(
                        'No manager found for employee {} {}'.format(employee.user.first_name, employee.user.last_name)
                    )
                    self.stdout.write("^^^^^^^^^^^^ WARNING ^^^^^^^^^^^^")
            else:
                if number == '1430': # Brenda Moore
                    pass
                elif number in (
                    '1552', # Stephanie Sheelar
                    '1559', # Josh Burstein
                    '1677', # Laura Campbell
                    '1793', # Emily Farrell
                    '1950', # Michael Wisth
                    '2168', # Betty Nielsen
                    '2206' # Matthew Brown
                ):
                    manager = Employee.objects.get(user__employee__number='1430') # Brenda
                else:
                    self.stdout.write("vvvvvvvvvvvv WARNING vvvvvvvvvvv")
                    self.stdout.write(
                        'No manager found for employee {} {}'.format(employee.user.first_name, employee.user.last_name)
                    )
                    self.stdout.write("^^^^^^^^^^^^ WARNING ^^^^^^^^^^^^")
            if not manager:
                employee.manager = None
                employee.save()
                self.stdout.write(
                    'Removed manager for employee {} {}'.format(employee.user.first_name, employee.user.last_name)
                )
            elif employee.manager != manager:
                employee.manager = manager
                employee.save()
                self.stdout.write(
                    'Added manager {} {} for employee {} {}'.format(manager.user.first_name, manager.user.last_name, employee.user.first_name, employee.user.last_name)
                )
        
        self.stdout.write(self.style.SUCCESS('Successfully imported users.'))