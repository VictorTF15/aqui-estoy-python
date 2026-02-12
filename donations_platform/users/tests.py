from django.test import TestCase
from django.urls import reverse
from .models import Usuarios, Donaciones, Casos

class UserTests(TestCase):

    def setUp(self):
        self.user = Usuarios.objects.create_user(
            nombres='Test',
            apellido_paterno='User',
            correo='testuser@example.com',
            contrasena='password123'
        )
        self.case = Casos.objects.create(
            id_beneficiario=self.user,
            titulo='Test Case',
            descripcion='This is a test case.',
            monto_objetivo=1000.00,
            monto_recaudado=0.00
        )
        self.donation = Donaciones.objects.create(
            id_donador=self.user,
            id_caso=self.case,
            monto=100.00
        )

    def test_user_creation(self):
        self.assertEqual(self.user.nombres, 'Test')
        self.assertEqual(self.user.apellido_paterno, 'User')
        self.assertEqual(self.user.correo, 'testuser@example.com')

    def test_case_creation(self):
        self.assertEqual(self.case.titulo, 'Test Case')
        self.assertEqual(self.case.monto_objetivo, 1000.00)

    def test_donation_creation(self):
        self.assertEqual(self.donation.monto, 100.00)
        self.assertEqual(self.donation.id_donador, self.user)

    def test_login_view(self):
        response = self.client.post(reverse('users:login'), {
            'correo': 'testuser@example.com',
            'contrasena': 'password123'
        })
        self.assertEqual(response.status_code, 200)

    def test_registration_view(self):
        response = self.client.post(reverse('users:register'), {
            'nombres': 'New',
            'apellido_paterno': 'User',
            'correo': 'newuser@example.com',
            'contrasena': 'password123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful registration

    def test_profile_view(self):
        self.client.login(correo='testuser@example.com', contrasena='password123')
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test User')