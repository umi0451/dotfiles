import unittest
unittest.defaultTestLoader.testMethodPrefix = 'should'
import json
import jsonpickle
import clckwrkbdgr.math
from clckwrkbdgr.math import Point, Size, Matrix

class MyVector(clckwrkbdgr.math.Vector):
	@property
	def first(self): return self.values[0]
	@first.setter
	def first(self, value): self.values[0] = value
	@property
	def second(self): return self.values[1]
	@second.setter
	def second(self, value): self.values[1] = value

class TestVector(unittest.TestCase):
	def should_create_vector(self):
		p = MyVector(1, 2)
		self.assertEqual(p.first, 1)
		self.assertEqual(p.second, 2)
		self.assertEqual(p[0], 1)
		self.assertEqual(p[1], 2)
		self.assertEqual(p, (1, 2))
	def should_call_setters(self):
		p = MyVector(1, 2)
		p.first = 2
		p.second = 3
		self.assertEqual(p[0], 2)
		self.assertEqual(p[1], 3)
	def should_serialize_vector(self):
		p = MyVector(1, 2)
		data = json.loads(jsonpickle.encode(p, unpicklable=False))
		self.assertEqual(data, [1, 2])
		self.assertEqual(jsonpickle.decode(jsonpickle.encode(p)), p)
	def should_deserialize_old_vector(self):
		q = jsonpickle.decode('{"py/newargs": {"py/tuple": [1, 2]}, "py/object": "clckwrkbdgr.test.test_math.MyVector", "py/seq": [1, 2]}')
		self.assertEqual(q.first, 1)
		self.assertEqual(q.second, 2)
	def should_create_vector_from_other_vector(self):
		p = MyVector(1, 2)
		o = MyVector(p)
		self.assertEqual(o.first, 1)
		self.assertEqual(o.second, 2)
	def should_compare_vectors(self):
		self.assertEqual(MyVector(1, 2), MyVector(1, 2))
		self.assertTrue(MyVector(1, 2) <= MyVector(1, 2))
		self.assertTrue(MyVector(1, 2) < MyVector(2, 2))
		self.assertTrue(MyVector(1, 2) < MyVector(1, 3))
	def should_add_vectors(self):
		self.assertEqual(MyVector(1, 2) + MyVector(2, 3), MyVector(3, 5))
	def should_subtract_vectors(self):
		self.assertEqual(MyVector(3, 5) - MyVector(2, 3), MyVector(1, 2))
	def should_multiply_vector(self):
		self.assertEqual(MyVector(1, 2) * 2, MyVector(2, 4))
	def should_divide_vector(self):
		self.assertEqual(MyVector(2, 4) / 2, MyVector(1, 2))
		self.assertEqual(MyVector(5, 6) // 3, MyVector(1, 2))

class TestMatrix(unittest.TestCase):
	def should_create_matrix(self):
		m = Matrix((2, 3), default='*')
		self.assertEqual(m.size(), (2, 3))
		self.assertEqual(m.width(), 2)
		self.assertEqual(m.height(), 3)
	def should_resize_matrix(self):
		m = Matrix((2, 3), default='*')
		self.assertEqual(m.size(), (2, 3))
		m.resize((3, 2), default='_')
		self.assertEqual(m.size(), (3, 2))
	def should_create_matrix_from_other_matrix(self):
		original = Matrix((2, 2))
		original.set_cell((0, 0), 'a')
		original.set_cell((0, 1), 'b')
		original.set_cell((1, 0), 'c')
		original.set_cell((1, 1), 'd')

		copy = Matrix(original)
		self.assertEqual(copy.cell((0, 0)), 'a')
		self.assertEqual(copy.cell((0, 1)), 'b')
		self.assertEqual(copy.cell((1, 0)), 'c')
		self.assertEqual(copy.cell((1, 1)), 'd')

		copy.set_cell((0, 0), '*')
		self.assertEqual(original.cell((0, 0)), 'a')

		original.set_cell((0, 0), '#')
		self.assertEqual(copy.cell((0, 0)), '*')
	def should_recognize_invalid_coords(self):
		m = Matrix((2, 2), default='*')
		self.assertTrue(m.valid((0, 0)))
		self.assertTrue(m.valid((0, 1)))
		self.assertTrue(m.valid((1, 0)))
		self.assertTrue(m.valid((1, 1)))
		self.assertFalse(m.valid((2, 2)))
		self.assertFalse(m.valid((-1, 0)))
	def should_get_cell_value(self):
		m = Matrix((2, 2), default='*')
		self.assertEqual(m.cell((0, 0)), '*')
		with self.assertRaises(KeyError):
			m.cell((-1, -1))
		with self.assertRaises(KeyError):
			m.cell((1, 10))
	def should_set_cell_value(self):
		m = Matrix((2, 2), default=' ')
		m.set_cell((0, 0), '*')
		self.assertEqual(m.cell((0, 0)), '*')
		with self.assertRaises(KeyError):
			m.set_cell((-1, -1), 'a')
		with self.assertRaises(KeyError):
			m.set_cell((1, 10), 'a')
	def should_iterate_over_indexes(self):
		m = Matrix((2, 2))
		indexes = ' '.join(''.join(map(str, index)) for index in m)
		self.assertEqual(indexes, '00 01 10 11')
