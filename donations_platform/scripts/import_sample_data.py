import os
import django
import random
from django.core.management import execute_from_command_line
from users.models import User, Role
from donations.models import Donation, Case

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'donations_platform.settings')
django.setup()

def create_sample_users(num_users=10):
    roles = Role.objects.all()
    users = []
    for _ in range(num_users):
        role = random.choice(roles)
        user = User.objects.create_user(
            username=f'user{_}',
            email=f'user{_}@example.com',
            password='password123',
            role=role
        )
        users.append(user)
    return users

def create_sample_cases(num_cases=5, users=None):
    cases = []
    for _ in range(num_cases):
        case = Case.objects.create(
            title=f'Sample Case {_}',
            description='This is a sample case description.',
            beneficiary=random.choice(users),
            target_amount=random.randint(1000, 5000),
            raised_amount=random.randint(0, 5000)
        )
        cases.append(case)
    return cases

def create_sample_donations(num_donations=20, users=None, cases=None):
    for _ in range(num_donations):
        Donation.objects.create(
            donor=random.choice(users),
            case=random.choice(cases),
            amount=random.randint(10, 500)
        )

def import_sample_data():
    print("Creating sample users...")
    users = create_sample_users()
    print("Creating sample cases...")
    cases = create_sample_cases(users=users)
    print("Creating sample donations...")
    create_sample_donations(users=users, cases=cases)
    print("Sample data imported successfully.")

if __name__ == '__main__':
    import_sample_data()