# yet another version of Schema
__all__ = ['ParaBase', 'Para', 'ParaField', 'F']

from collections import OrderedDict
from krux.types.null import Null
from .exceptions import *


class ParaBase(type):
    """Meta class for para"""
    def __new__(cls, name, bases, attrs, **kwargs):
        super_new = super().__new__

        # Ensure initialization is only performed for subclasses of Para
        # (Excluding Para class itself)
        parents = [b for b in bases if isinstance(b, ParaBase)]
        if not parents:
            return super_new(cls, name, bases, attrs)

        _fields = OrderedDict()

        # Create the class
        base_attrs = OrderedDict()
        for base in bases:
            if base_fields := getattr(base, '_fields', None):
                _fields.update(base_fields)

            for key, value in base.__dict__.items():
                if isinstance(value, ParaField):
                    _fields[key] = value
                elif key not in ('_fields', '__module__'):
                    base_attrs[key] = value

        to_pop = []
        for key, value in attrs.items():
            if isinstance(value, ParaField):
                _fields[key] = value
                to_pop.append(key)

        for key in to_pop:
            attrs.pop(key)

        module = attrs.pop('__module__')

        new_attrs = {
            '__module__': module,
            '_fields': _fields,
            **base_attrs,
            **attrs,
        }
        new_bases = tuple()

        new_class = super_new(cls, name, new_bases, new_attrs)
        return new_class


class Para(metaclass=ParaBase):
    # _fields will be modified/replaced by metaclass
    _fields = OrderedDict()

    def __init__(self, **kwargs):
        self._data = {}

        for key, field in self._fields.items():
            if field.default is not Null:
                self._data[key] = field.default

        for key, value in kwargs.items():
            if key in self._fields:
                self._data[key] = value

        self._validate_values()

    @classmethod
    def from_dict(cls, d):
        return cls(**d)

    def to_dict(self):
        return {field: self[field] for field in self._fields}

    def copy(self):
        return self.__class__.from_dict(self._data)

    def vary(self, **kwargs):
        return self.__class__.from_dict({**self._data, **kwargs})

    def update(self, key_or_dic, value=None):
        if isinstance(key_or_dic, dict):
            self._data.update(key_or_dic)
            self._validate_values(keys=set(key_or_dic.keys()))
        else:
            self._data[key_or_dic] = value
            self._validate_values(keys={key_or_dic})

    def _validate_values(self, keys=None):
        for key, field in self._fields.items():
            if keys is not None and key not in keys:
                continue

            if key not in self._data:
                if field.required:
                    raise MissingRequiredParaField(key)
            else:
                raw_value = self._data[key]
                if callable(raw_value):
                    raw_value = raw_value(self)
                field.validate(raw_value)

    def __len__(self):
        return len(self._fields)

    # dict compatible methods
    def keys(self):
        return self._fields.keys()

    def values(self):
        for field in self.keys():
            yield self[field]

    def items(self):
        for field in self.keys():
            yield field, self[field]

    def __getitem__(self, field):
        if field not in self._fields:
            raise InvalidParaField(f'Invalid para field {field} for {self}.')

        if field in self._data:
            value = self._data[field]
            if callable(value):
                return value(self)
            else:
                return value
        else:
            return None

    def __getattr__(self, field):
        return self[field]

    def __repr__(self):
        return f'<{self.__class__.__name__}>'

    def preview(self):
        pass


class ParaField:
    def __init__(self,
                 name='', desc='',
                 default=Null,
                 required=False,
                 vmin=None, vmax=None,
                 **kwargs):
        self.name = name
        self.default = default
        self.required = required
        self.desc = desc
        self.vmin = vmin
        self.vmax = vmax

    def validate(self, value):
        if self.vmin is not None and value < self.vmin:
            raise ParaFieldValueOutOfBound(f'{value} is too small for {self}, min value: {self.vmin}.')

        if self.vmax is not None and value > self.vmax:
            raise ParaFieldValueOutOfBound(f'{value} is too large for {self}, max value: {self.vmax}.')

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.name}>'


def F(name='', desc='',
      default=Null, required=False,
      vmin=None, vmax=None,
      **kwargs):
    # This shortcut function will become a factory for creating ParaField objects.
    # ParaField may be extended to more subclasses
    return ParaField(name=name, desc=desc,
                     default=default, required=required,
                     vmin=vmin, vmax=vmax,
                     **kwargs)