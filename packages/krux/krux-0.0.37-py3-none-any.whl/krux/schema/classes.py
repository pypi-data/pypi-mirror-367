__all__ = [
    'Schema',
    'SchemaItem',
    'NullDefaultValue',
]

from .exceptions import *


class NullDefaultValue:
    pass


class SchemaItem:
    def __init__(self, default=NullDefaultValue, required=False, desc=''):
        self.default = default
        self.required = required
        self.desc = desc


class Schema:
    Item = SchemaItem

    def __init__(self, dic=None):
        if not dic:
            dic = {}
        self._dic = dic

        self._required_keys = { key for (key, item) in self._dic.items() if item.required }
        self._defaults = {key: item.default for (key, item) in self._dic.items() if item.default is not NullDefaultValue}

    def validate(self, data):
        if not self:
            return {}

        missing_keys = self._required_keys - set(self._defaults.keys()) - set(data.keys())
        if len(missing_keys) > 0:
            raise SchemaMissingRequiredKeys(missing_keys)

        cleaned = self._defaults.copy()
        for key, value in data.items():
            # TODO: add type checking and other validations
            if key in self._dic:
                cleaned[key] = value

        return cleaned

    def __bool__(self):
        return bool(self._dic)
