from re				import compile as compile_re, search

from ..exception	import ValidateError
from ..context		import Context
from ..json_types	import Types
from ..utils		import assign_property_to_function

TYPES	= Types.TYPE_OBJECT,


@assign_property_to_function([["name", "properties"], ["version", 3]])
def properties(schema, schema_value, schema_parent, inst_value, context):
	context_sub	= Context(context, ("properties", Context.any_fail, schema_value, inst_value))
	return [[s, inst_value[k], Context(context_sub)] for k, s in schema_value.iteritems() if k in inst_value]

@assign_property_to_function([["name", "patternProperties"], ["version", 3]])
def patternProperties(schema, schema_value, schema_parent, inst_value, context):
	context_sub	= Context(context, ("patternProperties", Context.any_fail, schema_value, inst_value))
	return [
		[subschema, v, Context(context_sub)]

		for pattern, subschema in schema_value.iteritems()
		for k, v in inst_value.iteritems()
		if search(pattern, k)
	]



@assign_property_to_function([["name", "maxProperties"], ["version", 3]])
def maxProperties(schema, schema_value, schema_parent, inst_value, context):
	ret		= len(inst_value) > schema_value
	issue	= ValidateError("maxProperties", "properties :{} exceeds the number of allowed properties: {} for object: {}".format(len(inst_value), schema_value, inst_value)) if ret else None
	context.completed(issue)
	return []

@assign_property_to_function([["name", "minProperties"], ["version", 3]])
def minProperties(schema, schema_value, schema_parent, inst_value, context):
	ret		= len(inst_value) < schema_value
	issue	= ValidateError("minProperties", "properties :{} is under the number of allowed properties: {} for object: {}".format(len(inst_value), schema_value, inst_value)) if ret else None
	context.completed(issue)
	return []


@assign_property_to_function([["name", "required"], ["version", 3]])
def required(schema, schema_value, schema_parent, inst_value, context):
	ret		= set(schema_value) - set(inst_value)
	issue	= ValidateError("required", "properties :{} are missing required properties: {}".format(inst_value, list(ret))) if ret else None
	context.completed(issue)
	return []

@assign_property_to_function([["name", "additionalProperties"], ["version", 3]])
def additionalProperties(schema, schema_value, schema_parent, inst_value, context):
	sp		= set(schema_parent.get('properties', []))
	pp		= schema_parent.get("patternProperties", [])
	#TODO: compile this in the schema!!
	patt	= compile_re("|".join(pp)) #nice trick taken from https://github.com/Julian/jsonschema

	ret1	= set(inst_value) - sp
	ret		= [r for r in ret1 if not pp or not patt.search(r)]

	if schema_value is False:
		issue	= ValidateError("additionalProperties", "properties :{} are not defined in schema properties: {}, or in the patternProperties: {}".format(ret, sp, pp)) if ret else None
		context.completed(issue)
		return []
	elif schema_value is True:
		context.completed(None)
		return []
	elif isinstance(schema_value, dict):
		context_sub	= Context(context, ("additionalProperties", Context.any_fail, schema_value, inst_value))
		return [[schema_value, inst_value[k], Context(context_sub)] for k in ret]
	else:
		raise ValueError("unexpected type: {}, in: {}".format( schema_value, schema_parent) )


@assign_property_to_function([["name", "dependencies"], ["version", 3]])
def dependencies(schema, schema_value, schema_parent, inst_value, context):
	keys	= set(inst_value)
	props	= set(schema_value) & keys

	ret = [

			prop

			for prop in props
			if isinstance(schema_value[prop], list)
			if set(schema_value[prop]) - keys
	]

	issue	= ValidateError("dependencies", "properties :{} are missing required properties: {}".format(inst_value, list(ret))) if ret else None
	if issue is not None:
		context.completed(issue)
		return []
	else:
		subs = [

				schema_value[prop]

				for prop in props
				if not isinstance(schema_value[prop], list)
		]
		context_sub	= Context(context, ("dependencies", Context.any_fail, schema_value, inst_value))
		return [[sub_s, inst_value, Context(context_sub)] for sub_s in subs]


@assign_property_to_function([["name", "propertyNames"], ["version", 3]])
def propertyNames(schema, schema_value, schema_parent, inst_value, context):
	#TODO
	context.completed(None)
	return []


