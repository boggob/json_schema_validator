import types
import numbers
import collections


class Types(object):
	TYPE_NULL		= 0
	TYPE_BOOLEAN	= 1
	TYPE_INTEGER	= 2
	TYPE_NUMBER		= 3
	TYPE_OBJECT		= 4
	TYPE_STRING		= 5
	TYPE_ARRAY		= 6


	TYPES_FUNC_MAP	= [
		lambda val : isinstance(val, types.NoneType),
		lambda val : isinstance(val, types.BooleanType),
		lambda val : isinstance(val, numbers.Integral) and not isinstance(val, types.BooleanType),
		lambda val : isinstance(val, numbers.Real) and not isinstance(val, types.BooleanType),

		lambda val : isinstance(val, types.DictType),
		lambda val : isinstance(val, basestring),
		lambda val : isinstance(val, collections.Iterable) and not isinstance(val, basestring)  and not isinstance(val, types.DictType)
	]
	_TYPES_FUNC_MAP = list(enumerate(TYPES_FUNC_MAP))

	TYPES_STR_MAP	= [
		"null",
		"boolean",
		"integer",
		"number",
		"object",
		"string",
		"array",
	]
	_TYPES_STR_MAP = list(enumerate(TYPES_STR_MAP))


	@staticmethod
	def json_type(value):
		"""return most appropriate match"""
		types_	= [type_ for type_, func in Types._TYPES_FUNC_MAP if func(value)]
		if not types_:
			return None
		else:
			return types_[0]

	@staticmethod
	def str_type(value):
		"""return most appropriate match"""

		types_	= [type_ for type_, s in Types._TYPES_STR_MAP if s == value]
		if not types_:
			return None
		else:
			return types_[0]
