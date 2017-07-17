from .utils import dumps_safe

class SchemaBaseException(Exception):
	pass


class SchemaException(SchemaBaseException):
	def __init__(self, msg, inner=None):
		super(SchemaException, self).__init__(msg)
		self.inner = inner
	def __str__(self):
		return "{}:\n\t[{}]".format(self.message, self.inner)



class ValidateError(object):
	def __init__(self, type_, msg, traceback = None):
		#super(ValidateError, self).__init__(msg)
		self.message	= msg
		self.type		= type_
		self.traceback	= traceback


	def fmt(self, indent):
		return "\n{indent}Message: {message}\n{indent}ValidationType: {type_}\n{indent}traceback: {traceback}".format(
			indent		= "  " * indent,
			message		= self.message,
			type_		= self.type,
			traceback	= self.traceback
		)


	def serialise(self):
		return {
			"type"		: self.type,
			"message" 	: self.message,
			"traceback" : self.traceback
		}


	def __repr__(self):
		return "Validation failed: {}".format(self.fmt(1))

	def __str__(self):
		return repr(self)

class ValidateException(SchemaBaseException):
	def __init__(self, top, contexts):
		super(ValidateException, self).__init__("Validations have failed")
		self.top			= top
		self.contexts		= contexts



	def serialise(self, parent, children):
		return [error.serialise(parent, children) for error in self.contexts]


	def __repr__(self):
		return "ValidateException(\n  top={},\n  contexts=[{}\n  ]\n)".format(
			dumps_safe(self.top.serialise(False, False)),
			", ".join("\n    {}".format(dumps_safe(error.serialise(False, False))) for error in self.contexts)

		)

	def __str__(self):
		return repr(self)



class RefResolverError(SchemaException):
	pass
