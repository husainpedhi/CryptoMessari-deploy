"""Unit tests for Messari service helpers."""

import json
from datetime import date

import pytest

from app.services.messari_service import _safe_json, _parse_date, _get_nested


def test_safe_json_none():
    assert _safe_json(None) is None


def test_safe_json_string_passthrough():
    assert _safe_json("hello") == "hello"


def test_safe_json_list():
    result = _safe_json([1, 2, 3])
    assert json.loads(result) == [1, 2, 3]


def test_safe_json_dict():
    result = _safe_json({"key": "value"})
    assert json.loads(result) == {"key": "value"}


def test_parse_date_valid():
    result = _parse_date("2021-01-03")
    assert result == date(2021, 1, 3)


def test_parse_date_with_time():
    result = _parse_date("2021-01-03T00:00:00Z")
    assert result == date(2021, 1, 3)


def test_parse_date_none():
    assert _parse_date(None) is None


def test_parse_date_invalid():
    assert _parse_date("not-a-date") is None


def test_get_nested_found():
    obj = {"a": {"b": {"c": 42}}}
    assert _get_nested(obj, "a.b.c") == 42


def test_get_nested_missing():
    obj = {"a": {"b": {}}}
    assert _get_nested(obj, "a.b.c") is None


def test_get_nested_not_dict():
    obj = {"a": "string"}
    assert _get_nested(obj, "a.b") is None
