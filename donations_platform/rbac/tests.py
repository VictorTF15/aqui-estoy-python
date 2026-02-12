from django.test import TestCase
from django.urls import reverse
from .models import Role, Permission, RoleAssignment
from users.models import Usuarios

class RBACModelTests(TestCase):

    def setUp(self):
        self.role = Role.objects.create(name='Donor')
        self.permission = Permission.objects.create(name='Can make donations')
        self.user = Usuarios.objects.create_user(
            username='testuser',
            password='testpassword',
            correo='testuser@example.com'
        )
        RoleAssignment.objects.create(user=self.user, role=self.role)

    def test_role_creation(self):
        self.assertEqual(self.role.name, 'Donor')

    def test_permission_creation(self):
        self.assertEqual(self.permission.name, 'Can make donations')

    def test_role_assignment(self):
        assignment = RoleAssignment.objects.get(user=self.user)
        self.assertEqual(assignment.role, self.role)

    def test_user_permissions(self):
        self.user.permissions.add(self.permission)
        self.assertTrue(self.user.has_perm('Can make donations'))

class RBACViewTests(TestCase):

    def setUp(self):
        self.role = Role.objects.create(name='Beneficiary')
        self.user = Usuarios.objects.create_user(
            username='beneficiaryuser',
            password='beneficiarypassword',
            correo='beneficiaryuser@example.com'
        )
        RoleAssignment.objects.create(user=self.user, role=self.role)

    def test_access_protected_view(self):
        self.client.login(username='beneficiaryuser', password='beneficiarypassword')
        response = self.client.get(reverse('some_protected_view'))
        self.assertEqual(response.status_code, 200)

    def test_access_denied_without_permission(self):
        response = self.client.get(reverse('some_protected_view'))
        self.assertEqual(response.status_code, 403)