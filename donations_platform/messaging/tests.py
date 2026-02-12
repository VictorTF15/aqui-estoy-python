from django.test import TestCase
from django.urls import reverse
from .models import Conversaciones, Mensajes
from users.models import Usuarios

class MessagingTests(TestCase):

    def setUp(self):
        self.user1 = Usuarios.objects.create_user(
            nombres='John',
            apellido_paterno='Doe',
            correo='john@example.com',
            contrasena='password123'
        )
        self.user2 = Usuarios.objects.create_user(
            nombres='Jane',
            apellido_paterno='Smith',
            correo='jane@example.com',
            contrasena='password123'
        )
        self.conversacion = Conversaciones.objects.create(
            id_usuario1=self.user1,
            id_usuario2=self.user2
        )
        self.mensaje = Mensajes.objects.create(
            id_conversacion=self.conversacion,
            id_emisor=self.user1,
            contenido='Hello, Jane!'
        )

    def test_create_conversacion(self):
        self.assertEqual(Conversaciones.objects.count(), 1)

    def test_create_mensaje(self):
        self.assertEqual(Mensajes.objects.count(), 1)
        self.assertEqual(self.mensaje.contenido, 'Hello, Jane!')

    def test_mensaje_view(self):
        response = self.client.get(reverse('messaging:hilo_mensajes', args=[self.conversacion.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hello, Jane!')

    def test_conversaciones_view(self):
        response = self.client.get(reverse('messaging:conversaciones'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'John Doe')
        self.assertContains(response, 'Jane Smith')