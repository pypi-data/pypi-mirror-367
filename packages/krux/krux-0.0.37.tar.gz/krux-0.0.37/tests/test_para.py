import unittest
from krux.para import *
from krux.para.exceptions import *


class ParentPara(Para):
    a = F(name='A', default=100)
    b = F(name='B', required=True, vmin=200, vmax=400)


class ParentMixin:
    a = F(name='A')
    b = F(name='B')


class ChildPara(ParentPara):
    c = F(name='C')


class ChildParaByMixin(ParentMixin, Para):
    c = F(name='C')


class WithCompute(Para):
    a = F('A', default=100)
    b = F('B', default=lambda para: para.a * 2, vmin=200, vmax=400)


class MyTestCase(unittest.TestCase):
    # test meta class
    def test_items_removed_from_class_definition(self):
        self.assertIsNone(getattr(ParentPara, 'a', None))
        self.assertIsNone(getattr(ParentPara, 'b', None))

    def test_subclass(self):
        self.assertListEqual(list(ChildPara._fields.keys()), ['a', 'b', 'c'])

    def test_mixin(self):
        self.assertListEqual(list(ChildParaByMixin._fields.keys()), ['a', 'b', 'c'])

    # test creation, validation and conversion
    def test_init_and_validation(self):
        para1 = ParentPara(a=200, b=300)
        para2 = ParentPara(b=300)
        with self.assertRaises(MissingRequiredParaField):
            para3 = ParentPara()

        with self.assertRaises(ParaFieldValueOutOfBound):
            para4 = ParentPara(b=100)

        with self.assertRaises(ParaFieldValueOutOfBound):
            para4 = ParentPara(b=500)

    def test_from_dict_and_to_dict(self):
        d1 = {"a": 200, "b": 300, "c": 123}
        para1 = ChildPara.from_dict(d1)
        self.assertDictEqual(para1.to_dict(), d1)

    def test_copy_and_vary(self):
        raw = {"b": 300, "c": 123}
        para1 = ChildPara.from_dict(raw)
        para2 = para1.copy()
        self.assertDictEqual(para1.to_dict(), para2.to_dict())

        para3 = para1.vary(a=200, c=256)
        self.assertDictEqual(para3.to_dict(), {"a": 200, "b": 300, "c": 256})

    def test_with_compute(self):
        para1 = WithCompute()
        para2 = WithCompute(a=120)
        para3 = WithCompute(b=300)

        self.assertDictEqual(para1.to_dict(), {"a": 100, "b": 200})
        self.assertDictEqual(para2.to_dict(), {"a": 120, "b": 240})
        self.assertDictEqual(para3.to_dict(), {"a": 100, "b": 300})

        with self.assertRaises(ParaFieldValueOutOfBound):
            para_over = WithCompute(a=250)

    def test_getattr(self):
        para = WithCompute(a=120)
        self.assertEqual(para.a, 120)
        self.assertEqual(para.b, 240)

    def test_dict_compatible(self):
        para = WithCompute(a=120)
        self.assertEqual(para['a'], 120)
        self.assertEqual(para['b'], 240)

        self.assertSetEqual(set(para.keys()), {"a", "b"})
        self.assertSetEqual(set(para.values()), {120, 240})
        self.assertListEqual([(key, value) for key, value in para.items()], [("a", 120), ("b", 240)])

    def test_invalid_field(self):
        d = {"a": 200, "b": 300, "c": 123}
        para = ChildPara.from_dict(d)

        with self.assertRaises(InvalidParaField):
            para.x

        with self.assertRaises(InvalidParaField):
            para['x']


if __name__ == '__main__':
    unittest.main()
