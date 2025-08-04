import unittest
from krux.schema import *
from krux.schema.exceptions import *


class TestSchema(unittest.TestCase):
    def test_required_keys_and_default(self):
        schema = Schema({
            'a': Schema.Item(required=True),
            'b': Schema.Item(),
            'c': Schema.Item(default=1, required=True)
        })

        with self.assertRaises(SchemaMissingRequiredKeys):
            schema.validate({"c": 1})

        self.assertDictEqual(schema.validate({"a": 1}), {"a": 1, "c": 1})

        self.assertDictEqual(schema.validate({
            "a": 1, "b": 2, "c": 3, "d": 4
        }), {"a": 1, "b": 2, "c": 3})
