import importlib
import os
from pathlib import Path
from unittest import mock

import config.settings as project_settings
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, SimpleTestCase, TestCase
from django.urls import reverse


def read_project_settings_with_env(*names, **env_overrides):
    original_env = os.environ.copy()
    try:
        os.environ.clear()
        os.environ.update(original_env)
        for key, value in env_overrides.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        loaded_settings = importlib.reload(project_settings)
        return {name: getattr(loaded_settings, name) for name in names}
    finally:
        os.environ.clear()
        os.environ.update(original_env)
        importlib.reload(project_settings)


class ProjectSmokeTests(SimpleTestCase):
    def test_admin_route_exists(self):
        response = self.client.get(reverse("admin:login"))
        assert response.status_code == 200

    def test_mysql_engine_is_configured(self):
        assert settings.DATABASES["default"]["ENGINE"] == "django.db.backends.mysql"

    def test_mysql_charset_is_utf8mb4(self):
        assert settings.DATABASES["default"]["OPTIONS"]["charset"] == "utf8mb4"

    def test_allowed_hosts_can_be_loaded_from_environment(self):
        settings_values = read_project_settings_with_env(
            "ALLOWED_HOSTS",
            DJANGO_ALLOWED_HOSTS="example.com,www.example.com,127.0.0.1"
        )

        self.assertEqual(
            settings_values["ALLOWED_HOSTS"],
            ["example.com", "www.example.com", "127.0.0.1"],
        )

    def test_csrf_trusted_origins_can_be_loaded_from_environment(self):
        settings_values = read_project_settings_with_env(
            "CSRF_TRUSTED_ORIGINS",
            DJANGO_CSRF_TRUSTED_ORIGINS="https://example.com,https://www.example.com"
        )

        self.assertEqual(
            settings_values["CSRF_TRUSTED_ORIGINS"],
            ["https://example.com", "https://www.example.com"],
        )

    def test_static_root_targets_backend_staticfiles_directory(self):
        settings_values = read_project_settings_with_env("STATIC_ROOT", "BASE_DIR")

        self.assertEqual(
            settings_values["STATIC_ROOT"],
            Path(settings_values["BASE_DIR"]) / "staticfiles",
        )


class AdminChineseUiTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        user_model.objects.create_superuser(username="admin_zh", password="test321321")
        self.client = Client()

    def test_admin_index_uses_chinese_titles_for_apps_and_models(self):
        logged_in = self.client.login(username="admin_zh", password="test321321")
        self.assertTrue(logged_in)

        response = self.client.get(reverse("admin:index"), HTTP_HOST="localhost")

        self.assertEqual(response.status_code, 200)
        content = response.content.decode("utf-8")
        self.assertIn("菜单管理", content)
        self.assertIn("订单管理", content)
        self.assertIn("菜品分类", content)
        self.assertIn("菜品", content)
        self.assertIn("订单", content)
        self.assertNotIn("Catalog", content)
        self.assertNotIn("Orders", content)
        self.assertNotIn("Categorys", content)
        self.assertNotIn("Dishs", content)
