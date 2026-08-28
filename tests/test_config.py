"""Runtime configuration loading and the CORS credential guard."""

import dataclasses
import logging

import pytest

from accessai.config import (
    DEFAULT_CORS_ORIGINS,
    Settings,
    configure_logging,
    load_settings,
)


def test_defaults_are_same_origin_and_credential_free():
    settings = load_settings({})
    assert settings.cors_origins == DEFAULT_CORS_ORIGINS
    assert settings.cors_allow_credentials is False
    assert settings.environment == "development"
    assert settings.log_level == "INFO"


def test_origins_are_split_and_trimmed():
    settings = load_settings({"ACCESSAI_CORS_ORIGINS": " https://a.test , https://b.test "})
    assert settings.cors_origins == ("https://a.test", "https://b.test")


def test_blank_origin_list_falls_back_to_defaults():
    assert load_settings({"ACCESSAI_CORS_ORIGINS": "  ,  "}).cors_origins == DEFAULT_CORS_ORIGINS


def test_explicit_origins_may_carry_credentials():
    settings = load_settings(
        {
            "ACCESSAI_CORS_ORIGINS": "https://studio.example",
            "ACCESSAI_CORS_ALLOW_CREDENTIALS": "true",
        }
    )
    assert settings.cors_allow_credentials is True


def test_wildcard_origin_forces_credentials_off():
    """The Fetch spec forbids '*' with credentials; the pair must be unrepresentable."""
    settings = load_settings(
        {"ACCESSAI_CORS_ORIGINS": "*", "ACCESSAI_CORS_ALLOW_CREDENTIALS": "true"}
    )
    assert settings.allows_any_origin is True
    assert settings.cors_allow_credentials is False


def test_wildcard_downgrade_is_logged(caplog):
    with caplog.at_level(logging.WARNING, logger="accessai.config"):
        load_settings({"ACCESSAI_CORS_ORIGINS": "*", "ACCESSAI_CORS_ALLOW_CREDENTIALS": "1"})
    assert any("credentials are disabled" in record.message for record in caplog.records)


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("1", True),
        ("TRUE", True),
        ("yes", True),
        ("on", True),
        ("0", False),
        ("false", False),
        ("", False),
        ("maybe", False),
    ],
)
def test_boolean_parsing(raw, expected):
    settings = load_settings(
        {"ACCESSAI_CORS_ORIGINS": "https://a.test", "ACCESSAI_CORS_ALLOW_CREDENTIALS": raw}
    )
    assert settings.cors_allow_credentials is expected


def test_unprefixed_environment_is_honoured():
    """The shipped compose file sets ENVIRONMENT, not ACCESSAI_ENVIRONMENT."""
    assert load_settings({"ENVIRONMENT": "production"}).environment == "production"


def test_prefixed_environment_wins():
    settings = load_settings({"ENVIRONMENT": "production", "ACCESSAI_ENVIRONMENT": "staging"})
    assert settings.environment == "staging"


def test_log_level_is_normalised():
    assert load_settings({"ACCESSAI_LOG_LEVEL": "debug"}).log_level == "DEBUG"


def test_settings_are_immutable():
    with pytest.raises(dataclasses.FrozenInstanceError):
        load_settings({}).cors_allow_credentials = True


def test_settings_construct_with_no_arguments():
    assert Settings().cors_allow_credentials is False


def test_configure_logging_is_idempotent():
    configure_logging("INFO")
    before = len(logging.getLogger().handlers)
    configure_logging("INFO")
    assert len(logging.getLogger().handlers) == before
