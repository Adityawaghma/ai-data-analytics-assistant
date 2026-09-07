"""
Tests for src/updater.py
"""

import pytest
from unittest.mock import patch, Mock

from src.updater import check_updates


def _mock_response(tag_name, html_url="https://github.com/example/releases/tag/v1.2.3"):
    resp = Mock()
    resp.raise_for_status = Mock()
    resp.json.return_value = {"tag_name": tag_name, "html_url": html_url}
    return resp


@patch("src.updater.requests.get")
def test_update_available(mock_get):
    mock_get.return_value = _mock_response("v1.0.0")
    latest, url = check_updates(current="0.9.0")
    assert latest == "1.0.0"
    assert url == "https://github.com/example/releases/tag/v1.2.3"


@patch("src.updater.requests.get")
def test_already_up_to_date(mock_get):
    mock_get.return_value = _mock_response("v1.0.0")
    latest, url = check_updates(current="1.0.0")
    assert (latest, url) == (None, None)


@patch("src.updater.requests.get")
def test_current_is_newer_than_latest(mock_get):
    mock_get.return_value = _mock_response("v1.0.0")
    latest, url = check_updates(current="2.0.0")
    assert (latest, url) == (None, None)


@patch("src.updater.requests.get")
def test_offline_does_not_crash(mock_get):
    mock_get.side_effect = ConnectionError("no route to host")
    latest, url = check_updates(current="0.9.0")
    assert (latest, url) == (None, None)


@patch("src.updater.requests.get")
def test_malformed_response_does_not_crash(mock_get):
    resp = Mock()
    resp.raise_for_status = Mock()
    resp.json.return_value = {}
    mock_get.return_value = resp
    latest, url = check_updates(current="0.9.0")
    assert (latest, url) == (None, None)


@patch("src.updater.requests.get")
def test_http_error_does_not_crash(mock_get):
    resp = Mock()
    resp.raise_for_status.side_effect = Exception("404 Not Found")
    mock_get.return_value = resp
    latest, url = check_updates(current="0.9.0")
    assert (latest, url) == (None, None)
