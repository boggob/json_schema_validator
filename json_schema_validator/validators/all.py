from logging		import getLogger
from sys			import exc_info
from traceback		import extract_tb

from ..exception	import ValidateError
from ..context		import Context
from ..json_types	import Types
from ..utils		import assign_property_to_function

logger = getLogger('json_schema_validator.ref_resolver')
debug, info, warning, error = logger.debug, logger.info, logger.warning, logger.error


TYPES	= None,

@assign_property_to_function([["name", "enum"], ["version", 3]])
def enum(schema, schema_value, schema_parent, inst_value, context):
	ret		= inst_value not in schema_value
	issue	= ValidateError("enum", "Value: {}, is not one of accepted enum values: {}".format(inst_value, schema_value)) if ret else None
	context.completed(issue)
	return []

@assign_property_to_function([["name", "const"], ["version", 3]])
def const(schema, schema_value, schema_parent, inst_value, context):
	#TODO
	context.completed(None)
	return []

@assign_property_to_function([["name", "type"], ["version", 3]])
def type_(schema, schema_value, schema_parent, inst_value, context):
	type_data	= Types.json_type(inst_value)
	type_schema = [Types.str_type(schema_value)] if not isinstance(schema_value, list) else  [Types.str_type(t) for t in schema_value]
	ret		= type_data not in type_schema and not (type_data == Types.TYPE_INTEGER and Types.TYPE_NUMBER in type_schema)
	issue	= ValidateError("type",  "type of value :{} is not one of the allowed types: {}".format(inst_value, schema_value)) if ret else None
	context.completed(issue)
	return []

@assign_property_to_function([["name", "allOf"], ["version", 3]])
def allOf(schema, schema_value, schema_parent, inst_value, context):
	context_sub	= Context(context, ("allOf", Context.any_fail, schema_value, inst_value))
	return [[s, inst_value, Context(context_sub)] for s in schema_value]

@assign_property_to_function([["name", "anyOf"], ["version", 3]])	
def anyOf(schema, schema_value, schema_parent, inst_value, context):
	context_sub	= Context(context, ("anyOf", Context.all_fail, schema_value, inst_value))
	return [[s, inst_value, Context(context_sub)] for s in schema_value]

@assign_property_to_function([["name", "oneOf"], ["version", 3]])	
def oneOf(schema, schema_value, schema_parent, inst_value, context):
	context_sub	= Context(context, ("oneOf", Context.one_pass, schema_value, inst_value))
	return [[s, inst_value, Context(context_sub)] for s in schema_value]

@assign_property_to_function([["name", "not"], ["version", 3]])	
def not_(schema, schema_value, schema_parent, inst_value, context):	
	context_sub	= Context(context, ("not", Context.no_pass, schema_value, inst_value))
	return [[schema_value, inst_value, Context(context_sub)]]
	
	
@assign_property_to_function([["name", "$ref"], ["version", 3], ["sortorder", -1]])
def ref(schema, schema_value, schema_parent, inst_value, context):	
	if schema_value == "#":
		context_sub	= Context(context, ("ref", Context.any_fail, context.frame, inst_value))
		return [[context.frame, inst_value, Context(context_sub)]]
	else:
		try:
			schema_new, _frame, _id	= schema.ref_resolver.ref(schema_value, context.frame, context.id)

			context_sub	= Context(context, ("ref", Context.any_fail, schema_new, inst_value), frame = _frame)			
			context_sub.set_id(_id) 
			return [[schema_new, inst_value, Context(context_sub)]]
		except Exception, e:	
			import traceback
		
			print "%%", traceback.format_exc()
			
			context.completed(ValidateError("$ret", "unresolved reference: {}, error: {}".format(schema_value, e), extract_tb(exc_info()[2])))
			return []

@assign_property_to_function([["name", "id"], ["version", 3], ["sortorder", -2]])
def id_(schema, schema_value, schema_parent, inst_value, context):	
	#TODO: don't like arbitrarily mutating this object here	
	new_id = schema.ref_resolver.id_cache(context.id, schema_value, schema_parent)
	info('{"new_id":"%s", "old_id":"%s"}', new_id, context.id)
	context.set_id(new_id) 
	return []





