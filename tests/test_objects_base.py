"""
    Tests for botogram/objects/base.py

    Copyright (c) 2015 Pietro Albini <pietro@pietroalbini.io>
    Released under the MIT license
"""

import pytest

import botogram.objects.base as objectsbase


class AnObject(objectsbase.BaseObject):

    required = {
        "test1": int,
    }


class ObjectToTest(objectsbase.BaseObject):

    required = {
        "test1": int,
        "test2": AnObject,
    }
    optional = {
        "test3": str,
        "test4": objectsbase.multiple(AnObject),
        "test5": objectsbase.one_of(AnObject, int),
    }


def test_object_creation():
    # First of all provide everything needed plus an optional field
    obj = ObjectToTest({"test1": 42, "test2": {"test1": 98}, "test3": "test"})
    assert obj.test1 == 42
    assert isinstance(obj.test2, AnObject)
    assert obj.test2.test1 == 98
    assert obj.test3 == "test"

    # Next, try to leave out the optional field
    obj = ObjectToTest({"test1": 42, "test2": {"test1": 98}})
    assert obj.test3 is None

    # And then try to leave out something required
    with pytest.raises(ValueError):
        obj = ObjectToTest({"test1": 42})

    # Or to provide an invalid type
    with pytest.raises(ValueError):
        obj = ObjectToTest({"test1": 42, "test2": "nope"})
    with pytest.raises(ValueError):
        obj = ObjectToTest({"test1": "nope", "test2": {"test1": 98}})

    # And then provide multiple things
    obj = ObjectToTest({"test1": 42, "test2": {"test1": 98}, "test4":
                       [{"test1": 1}, {"test1": 2}, {"test1": 3}]})
    assert obj.test4[0].test1 == 1
    assert obj.test4[1].test1 == 2
    assert obj.test4[2].test1 == 3

    # Multiple tests for multiple values
    obj1 = ObjectToTest({"test1": 42, "test2": {"test1": 98}, "test5":
                        {"test1": 98}})
    obj2 = ObjectToTest({"test1": 42, "test2": {"test1": 98}, "test5": 1})
    assert isinstance(obj1.test5, AnObject)
    assert obj1.test5.test1 == 98
    assert obj2.test5 == 1


def test_provide_api(api):
    data = {"test1": 42, "test2": {"test1": 98}, "test4": [{"test1": 1},
           {"test1": 2}, {"test1": 3}], "test5": {"test1": 4}}

    # Try either to provide the API at initialization time, or after
    obj1 = ObjectToTest(data, api)
    obj2 = ObjectToTest(data)
    obj2.set_api(api)

    for obj in obj1, obj2:
        assert obj._api == api
        assert obj.test2._api == api
        assert obj.test4[0]._api == api
        assert obj.test5._api == api


def test_serialize():
    data = {"test1": 42, "test2": {"test1": 98}, "test4": [{"test1": 1},
           {"test1": 2}, {"test1": 3}], "test5": {"test1": 4}}

    # Try to load this and serialize it
    assert ObjectToTest(data).serialize() == data