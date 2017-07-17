from logging		import getLogger, DEBUG
from json			import loads


from .context		import Context
from .exception		import SchemaException, ValidateException
from .json_types	import Types
from .ref_resolver	import RefResolverBase, RefResolverFileUTF8
from .validators	import VALIDATORS


logger = getLogger('json_schema_validator.schema')
debug, info, warning, error = logger.debug, logger.info, logger.warning, logger.error

#TODO: need to do infinite recursion checks for the $ref flattening

class Schema(object):
	@staticmethod
	def ref_resolver_provider(ref_resolver_class = None):
		if ref_resolver_class is None:
			ref_resolver_class = RefResolverFileUTF8
		elif isinstance(ref_resolver_class, RefResolverBase):	
			return ref_resolver_class
		elif not issubclass(ref_resolver_class, RefResolverBase):
			raise SchemaException("Provided ref resolver: {} is not an instance of RefResolverBase".format(type(ref_resolver_class).__name__))
		return ref_resolver_class

	@staticmethod
	def from_file(filename, ref_resolver_class = None):
		ref_resolver_class	= Schema.ref_resolver_provider(ref_resolver_class)
		ref_resolver		= ref_resolver_class(filename)
		return Schema(ref_resolver.schema, ref_resolver)

	@staticmethod
	def from_str(val, ref_resolver_class = None):
		ref_resolver_class = Schema.ref_resolver_provider(ref_resolver_class)

		try:
			schema	= loads(val)
		except Exception,e :
			raise SchemaException("JSON serialisation error: {}".format(e), e)

		ref_resolver		= ref_resolver_class(schema)	
		return Schema(ref_resolver.schema, ref_resolver)

	@staticmethod
	def from_json(schema, ref_resolver_class = None):
		ref_resolver_class	= Schema.ref_resolver_provider(ref_resolver_class)
		ref_resolver		= ref_resolver_class(schema)
		return Schema(ref_resolver.schema, ref_resolver)
	

	def __init__(self, schema, ref_resolver):
		self.schema			= schema
		self.ref_resolver	= ref_resolver
		
		self.ref_resolver.absolute_ids_to_cache(self.schema)		

	def validate(self, data, raise_if_fail = True):
		try:
			context_root	= Context(None, (None, None, self.schema, data), frame = self.schema)
			stack			= [(self.schema, data, context_root)]

			while stack:
				schema_parent, inst_value, context	= stack.pop()
				type_data							= Types.json_type(inst_value)

				if type_data is None:
					raise ValueError("Invalid type of instance data: {}, {}".format(type(inst_value), inst_value))

				validators = VALIDATORS.get(None, []) + VALIDATORS.get(type_data, [])
				if not(validators):
					warning('{"message": "No validators", "type": %s, "value":%s,"context":%s}', type_data, str(inst_value), context)

				next_items	= []
				for validator in validators:
					if validator.name in schema_parent:
						schema_value	= schema_parent[validator.name] if isinstance(schema_parent, dict) else validator.name == schema_parent

						if logger.isEnabledFor(DEBUG):
							debug(
								'{{ "type": %s, "validator": %s, "value": %s, "schema": %s, "schema_parent": %s, "context": %s}}',
								str(Types.TYPES_STR_MAP[type_data]),
								validator.name,
								repr(inst_value),
								repr(schema_value),
								repr(schema_parent),
								context.fmt(True),
							)


						cont			= validator(self, schema_value, schema_parent, inst_value, context)
						next_items.extend(cont)

						#if there are any other tests in the object they get nuked by the $ref
						if validator.name == "$ref":
							break


				if not context.failed:
					stack.extend(next_items)

				if not context.complete and not next_items:
					context.completed(None, force = True)


		except ValidateException, e:
			if not raise_if_fail:
				return e
			else:
				raise
