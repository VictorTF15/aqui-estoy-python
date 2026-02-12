from django.test import TestCase
from django.urls import reverse
from .models import Donaciones, Casos
from users.models import Usuarios

class DonacionesTests(TestCase):

    def setUp(self):
        self.user = Usuarios.objects.create_user(
            nombres='Test',
            apellido_paterno='User',
            correo='testuser@example.com',
            contrasena='securepassword'
        )
        self.caso = Casos.objects.create(
            id_beneficiario=self.user,
            titulo='Test Case',
            descripcion='This is a test case.',
            monto_objetivo=1000.00,
            monto_recaudado=0.00
        )
        self.donacion = Donaciones.objects.create(
            id_donador=self.user,
            id_caso=self.caso,
            monto=100.00
        )

    def test_donacion_creation(self):
        self.assertEqual(self.donacion.monto, 100.00)
        self.assertEqual(self.donacion.id_donador, self.user)
        self.assertEqual(self.donacion.id_caso, self.caso)

    def test_donaciones_list_view(self):
        response = self.client.get(reverse('donations:lista_donaciones'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Case')
        self.assertContains(response, '100.00')

    def test_donacion_detail_view(self):
        response = self.client.get(reverse('donations:detalle_donacion', args=[self.donacion.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Case')
        self.assertContains(response, '100.00')