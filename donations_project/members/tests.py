from django.test import TestCase
from django.urls import reverse
from .models import Usuario, Caso

class FeedViewTests(TestCase):

    def setUp(self):
        self.usuario = Usuario.objects.create(
            nombres='Juan',
            apellido_paterno='Pérez',
            correo='juan.perez@example.com'
        )
        self.caso_reciente = Caso.objects.create(
            titulo='Caso de prueba',
            descripcion='Descripción del caso de prueba.',
            fecha_creacion='2023-01-01',
            usuario=self.usuario
        )
        self.historial_caso = Caso.objects.create(
            titulo='Caso antiguo',
            descripcion='Descripción de un caso antiguo.',
            fecha_creacion='2022-01-01',
            usuario=self.usuario
        )

    def test_feed_view_status_code(self):
        response = self.client.get(reverse('members:feed'))
        self.assertEqual(response.status_code, 200)

    def test_feed_view_template_used(self):
        response = self.client.get(reverse('members:feed'))
        self.assertTemplateUsed(response, 'members/feed.html')

    def test_feed_view_context(self):
        response = self.client.get(reverse('members:feed'))
        self.assertIn('usuario', response.context)
        self.assertIn('casos_recientes', response.context)
        self.assertIn('historial', response.context)

    def test_feed_view_displays_recent_cases(self):
        response = self.client.get(reverse('members:feed'))
        self.assertContains(response, self.caso_reciente.titulo)
        self.assertContains(response, self.caso_reciente.descripcion)

    def test_feed_view_displays_history(self):
        response = self.client.get(reverse('members:feed'))
        self.assertContains(response, self.historial_caso.titulo)