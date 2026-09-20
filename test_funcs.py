import json
import unittest
from typing import Any

from otsucfgmng import get_dict_keys_places, is_support_json_dump, support_json_dump
from otsutil import OtsuNone


class SupportJsonDump:
    def __str__(self) -> str:
        return "SupportJsonDump"

    def to_json(self) -> Any:
        return {"classname": "SupportJsonDump"}


class NotSupportJsonDump:
    def __str__(self) -> str:
        return "NotSupportJsonDump"


sample_dict1 = {
    "name": "Otsuhachi",
    "data": {
        "age": 28,
        "H_W": {
            "height": 167,
            "weight": 81,
        },
    },
}
sample_dict2 = {
    "name": "Otsuhachi",
    "data": {
        "age": 28,
        "H_W": {"height": 167, "weight": 81},
    },
    "support": SupportJsonDump(),
}
sample_dict3 = {
    "name": "Otsuhachi",
    "data": {
        "age": 28,
        "H_W": {"height": 167, "weight": 81},
    },
    "support": NotSupportJsonDump(),
}


class TestCase(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def test_get_dict_keys_places(self) -> None:
        returns = list(get_dict_keys_places(sample_dict1))
        expect = [
            ("name", "Otsuhachi", None),
            ("age", 28, ["data"]),
            ("height", 167, ["data", "H_W"]),
            ("weight", 81, ["data", "H_W"]),
        ]

        self.assertEqual(returns, expect)

    def test_is_support_json_dump(self) -> None:
        sjd = SupportJsonDump()
        self.assertEqual(is_support_json_dump(sjd), True)
        nsjd = NotSupportJsonDump()
        self.assertEqual(is_support_json_dump(nsjd), False)
        for sample_value in ("json", 0, 0, 0, True, None, OtsuNone):
            self.assertEqual(is_support_json_dump(sample_value), False)

    def test_support_json_dump(self) -> None:
        # sd2
        with self.assertRaisesRegex(TypeError, "not JSON serializable"):
            json.dumps(sample_dict2)

        expect = '{"name": "Otsuhachi", "data": {"age": 28, "H_W": {"height": 167, "weight": 81}}, "support": {"classname": "SupportJsonDump"}}'
        dump = json.dumps(sample_dict2, default=support_json_dump)
        self.assertEqual(dump, expect)

        # sd3
        with self.assertRaisesRegex(TypeError, "not JSON serializable"):
            json.dumps(sample_dict3)

        expect = '{"name": "Otsuhachi", "data": {"age": 28, "H_W": {"height": 167, "weight": 81}}, "support": "NotSupportJsonDump"}'
        dump = json.dumps(sample_dict3, default=support_json_dump)
        self.assertEqual(dump, expect)


if __name__ == "__main__":
    unittest.main()
