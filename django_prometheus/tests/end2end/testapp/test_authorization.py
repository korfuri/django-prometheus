import base64

from django.test import TestCase, Client
from django.conf import settings


EXPECTED_USERNAME = "prometheus"
EXPECTED_PASSWORD = "secret"


class TestProtectedMetrics(TestCase):
    def test_credentials_not_set__success_response(self):
        c = Client()
        # Assure there's no expected token
        setattr(settings, "DJANGO_PROMETHEUS_AUTHORIZATION_USERNAME", None)
        setattr(settings, "DJANGO_PROMETHEUS_AUTHORIZATION_PASSWORD", None)

        response = c.get("/metrics")
        self.assertEqual(200, response.status_code)
        self.assertContains(response, "python_info{")

    def test_bad_auth_string__bad_request_response(self):
        c = Client(HTTP_AUTHORIZATION=f"Basic d3Jvbmc=")
        setattr(settings, "DJANGO_PROMETHEUS_AUTHORIZATION_USERNAME", EXPECTED_USERNAME)
        setattr(settings, "DJANGO_PROMETHEUS_AUTHORIZATION_PASSWORD", EXPECTED_PASSWORD)

        response = c.get("/metrics")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(response.content), 0)

    def test_bad_credentials__unauthorized_response(self):
        c = Client(HTTP_AUTHORIZATION=f"Basic dXNlcjp3cm9uZ3Bhc3M=")
        setattr(settings, "DJANGO_PROMETHEUS_AUTHORIZATION_USERNAME", EXPECTED_USERNAME)
        setattr(settings, "DJANGO_PROMETHEUS_AUTHORIZATION_PASSWORD", EXPECTED_PASSWORD)

        response = c.get("/metrics")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(len(response.content), 0)

    def test_correct_credentials__success_response(self):
        auth_string = f'{EXPECTED_USERNAME}:{EXPECTED_PASSWORD}'
        expected_auth = base64.b64encode(auth_string.encode()).decode()
        c = Client(HTTP_AUTHORIZATION=f"Basic {expected_auth}")
        setattr(settings, "DJANGO_PROMETHEUS_AUTHORIZATION_USERNAME", EXPECTED_USERNAME)
        setattr(settings, "DJANGO_PROMETHEUS_AUTHORIZATION_PASSWORD", EXPECTED_PASSWORD)

        response = c.get("/metrics")
        self.assertEqual(response.status_code, 200)
