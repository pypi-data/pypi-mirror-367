import pytest

from atptools import Records

record_list: list[dict] = [
    {
        "first_name": "Sherlock",
        "last_name": "Holmes",
        "age": 45,
        "email": "sherlock.holmes@gmail.com",
    },
    {
        "first_name": "John",
        "last_name": "Watson",
        "age": 50,
        "email": "john.watson@gmail.com",
    },
    {
        "first_name": "John",
        "last_name": "Malcovich",
        "age": 50,
        "email": "john.malcovich@gmail.com",
    },
    {
        "first_name": "Agatha",
        "last_name": "Christie",
        "age": 60,
        "email": "agatha.christie@gmail.com",
    },
]


def test_commare_records():
    records = Records(record_list)
    assert records == record_list


def test_commare_records_and_dict_level_1():
    records = Records(record_list)
    with pytest.raises(Exception) as exc_info:
        records.to_dict(["first_name"])
    assert isinstance(exc_info.value, Exception)


def test_commare_records_and_dict_level_2():
    records = Records(record_list)
    ret: dict = records.to_dict(["first_name", "last_name"])
    assert ret == {
        "Agatha": {
            "Christie": {
                "age": 60,
                "email": "agatha.christie@gmail.com",
                "first_name": "Agatha",
                "last_name": "Christie",
            }
        },
        "John": {
            "Malcovich": {
                "age": 50,
                "email": "john.malcovich@gmail.com",
                "first_name": "John",
                "last_name": "Malcovich",
            },
            "Watson": {
                "age": 50,
                "email": "john.watson@gmail.com",
                "first_name": "John",
                "last_name": "Watson",
            },
        },
        "Sherlock": {
            "Holmes": {
                "age": 45,
                "email": "sherlock.holmes@gmail.com",
                "first_name": "Sherlock",
                "last_name": "Holmes",
            }
        },
    }


def test_commare_records_and_dict_level_3():
    records = Records(record_list)
    ret: dict = records.to_dict(["first_name", "last_name", "age"])
    assert ret == {
        "Agatha": {
            "Christie": {
                60: {
                    "age": 60,
                    "email": "agatha.christie@gmail.com",
                    "first_name": "Agatha",
                    "last_name": "Christie",
                }
            }
        },
        "John": {
            "Malcovich": {
                50: {
                    "age": 50,
                    "email": "john.malcovich@gmail.com",
                    "first_name": "John",
                    "last_name": "Malcovich",
                }
            },
            "Watson": {
                50: {
                    "age": 50,
                    "email": "john.watson@gmail.com",
                    "first_name": "John",
                    "last_name": "Watson",
                }
            },
        },
        "Sherlock": {
            "Holmes": {
                45: {
                    "age": 45,
                    "email": "sherlock.holmes@gmail.com",
                    "first_name": "Sherlock",
                    "last_name": "Holmes",
                }
            }
        },
    }
