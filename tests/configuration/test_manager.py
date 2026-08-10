"""Testes do ConfigurationManager."""

import os

import pytest

from app.configuration.manager import ConfigurationManager
from app.configuration.errors import ConfigValidationError
from app.configuration.secrets import mask_dict


def test_load_defaults():
    manager = ConfigurationManager(environment="development")
    config = manager.load()
    assert config.application.name == "Yelena"
    assert config.application.environment == "development"
    assert config.application.debug is True
    assert config.core.shutdown_timeout == 30.0


def test_production_debug_forbidden(monkeypatch):
    manager = ConfigurationManager(environment="production")
    # force debug via memory override after would fail validation
    config = manager.load()
    assert config.application.debug is False


def test_secret_masking():
    data = {"token": "abc123", "name": "yelena", "nested": {"api_key": "secret"}}
    masked = mask_dict(data)
    assert masked["token"] == "********"
    assert masked["name"] == "yelena"
    assert masked["nested"]["api_key"] == "********"


def test_override():
    manager = ConfigurationManager(environment="testing")
    manager.load()
    manager.override("core", "shutdown_timeout", 15.0)
    assert manager.config.core.shutdown_timeout == 15.0


def test_masked_snapshot():
    manager = ConfigurationManager(environment="testing")
    manager.load()
    snap = manager.masked_snapshot()
    assert "application" in snap
    assert "secrets" in snap
