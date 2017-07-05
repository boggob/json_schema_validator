from ..exception	import ValidateError
from ..context		import Context
from ..json_types	import Types
from ..utils		import assign_property_to_function



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
	
	
@assign_property_to_function([["name", "$ref"], ["version", 3]])
def ref(schema, schema_value, schema_parent, inst_value, context):	
	if schema_value == "#":
		context_sub	= Context(context, ("ref", Context.any_fail, schema_value, inst_value))
		return [[schema.schema, inst_value, Context(context_sub)]]
	else:
		try:
			
			context_sub	= Context(context, ("ref", Context.any_fail, schema_value, inst_value))
			return [[schema.ref_resolver(schema.schema).ref(schema_value, None, schema_parent.get("id")), inst_value, Context(context_sub)]]
		except Exception, e:	
			context.completed(ValidateError("$ret", "unresolved reference: {}, error: {}".format(schema_value, e)))
			return []






