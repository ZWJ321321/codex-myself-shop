from django.conf import settings
from django.test import SimpleTestCase
from django.urls import reverse


class ProjectSmokeTests(SimpleTestCase):
    def test_admin_route_exists(self):
        response = self.client.get(reverse("admin:login"))
        assert response.status_code == 200

    def test_mysql_engine_is_configured(self):
        assert settings.DATABASES["default"]["ENGINE"] == "django.db.backends.mysql"
