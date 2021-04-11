from django.test import TestCase, Client
from django.conf import settings


class TestProtectedMetrics(TestCase):
    def test_token_not_set__success_response(self):
        c = Client()
        # Assure there's no expected token
        setattr(settings, "DJANGO_PROMETHEUS_AUTHORIZATION_TOKEN", None)

        response = c.get("/metrics")
        self.assertEqual(200, response.status_code)
        self.assertContains(response, "python_info{")

    def test_wrong_token__unauthorized_response(self):
        expected_token = "top_secret_string"
        c = Client(HTTP_AUTHORIZATION="Bearer incorrec_value_for_token")
        setattr(settings, "DJANGO_PROMETHEUS_AUTHORIZATION_TOKEN", expected_token)

        response = c.get("/metrics")
        self.assertEqual(len(response.content), 0)

    def test_correct_token_wrong_type__bad_request_response(self):
        expected_token = "top_secret_string"
        c = Client(HTTP_AUTHORIZATION=f"WRONG_TYPE {expected_token}")
        setattr(settings, "DJANGO_PROMETHEUS_AUTHORIZATION_TOKEN", expected_token)
        response = c.get("/metrics")
        self.assertEqual(response.status_code, 400)

    def test_correct_token_and_type__success_response(self):
        expected_token = "top_secret_string"
        c = Client(HTTP_AUTHORIZATION=f"Bearer {expected_token}")
        setattr(settings, "DJANGO_PROMETHEUS_AUTHORIZATION_TOKEN", expected_token)
        response = c.get("/metrics")
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(len(response.content), 0)
