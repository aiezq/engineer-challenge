import os
import unittest
from unittest.mock import patch

from src.config import (
    APP_ENV_PRODUCTION,
    APP_ENV_TEST,
    DEFAULT_DEV_JWT_SECRET_KEY,
    get_settings,
)


class ConfigTests(unittest.TestCase):
    def tearDown(self) -> None:
        get_settings.cache_clear()

    def test_dev_and_test_env_use_stable_secret_default(self) -> None:
        get_settings.cache_clear()
        with patch.dict(os.environ, {"APP_ENV": APP_ENV_TEST}, clear=True):
            settings = get_settings()

        self.assertEqual(settings.jwt_secret_key, DEFAULT_DEV_JWT_SECRET_KEY)
        self.assertTrue(settings.rate_limit_fail_open)

    def test_production_requires_explicit_jwt_secret(self) -> None:
        get_settings.cache_clear()
        with patch.dict(os.environ, {"APP_ENV": APP_ENV_PRODUCTION}, clear=True):
            with self.assertRaisesRegex(ValueError, "JWT_SECRET_KEY is required"):
                get_settings()
