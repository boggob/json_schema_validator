from ..exception	import ValidateError
from ..context		import Context
from ..json_types	import Types
from ..utils		import hashable, assign_property_to_function

TYPES	= Types.TYPE_ARRAY,
	

@assign_property_to_function([["name", "items"], ["version", 3]])
def items(schema, schema_value, schema_parent, inst_value, context):
	if Types.json_type(schema_value) == Types.TYPE_OBJECT:
		context_sub	= Context(context, ("items", Context.any_fail, schema_value, inst_value))
		return [[schema_value, i, Context(context_sub)] for i in inst_value]
	else:
		context_sub	= Context(context, ("items", Context.any_fail, schema_value, inst_value))
		return [[s, i, Context(context_sub)] for i, s in zip(inst_value, schema_value)]
		
@assign_property_to_function([["name", "additionalItems"], ["version", 3]])
def additionalItems(schema, schema_value, schema_parent, inst_value, context):
	s_items		= schema_parent.get("items", {})
	len_items	= len(s_items)
	if Types.json_type(s_items) == Types.TYPE_ARRAY:
		if Types.json_type(schema_value) == Types.TYPE_OBJECT:
			context_sub	= Context(context, ("items", Context.any_fail, schema_value, inst_value))
			
			return [[schema_value, i, Context(context_sub)] for i in inst_value[len_items:]]
		else:
			ret		= Types.json_type(schema_value) == Types.TYPE_BOOLEAN and not schema_value and len(inst_value) > len_items 
			issue	= ValidateError("additionalItems", "No additional items allowed, instance length: {}, schema length: {}".format(len(inst_value), len_items)) if ret else None
			context.completed(issue)	
			return []
	else:		
		context.completed(None)	
		return []

		
@assign_property_to_function([["name", "contains"], ["version", 3]])
def contains(schema, schema_value, schema_parent, inst_value, context):
	context_sub	= Context(context, ("contains", Context.all_fail, schema_value, inst_value))
	return [[schema_value, i, Context(context_sub)] for i in inst_value]
	
		
		
		
@assign_property_to_function([["name", "maxItems"], ["version", 3]])
def maxItems(schema, schema_value, schema_parent, inst_value, context):
	ret		= len(inst_value) > schema_value
	issue	= ValidateError("maxItems", "length :{} is longer than allowed length: {} for array: {}".format(len(inst_value), schema_value, inst_value)) if ret else None
	context.completed(issue)	
	return []
	
@assign_property_to_function([["name", "minItems"], ["version", 3]])
def minItems(schema, schema_value, schema_parent, inst_value, context):
	ret		= len(inst_value) < schema_value
	issue	= ValidateError("minItems", "length :{} is shorter than allowed length: {} for array: {}".format(len(inst_value), schema_value, inst_value)) if ret else None
	context.completed(issue)	
	return []

				
	
	
	
@assign_property_to_function([["name", "uniqueItems"], ["version", 3]])
def uniqueItems(schema, schema_value, schema_parent, inst_value, context):
	ret		= schema_value and len(inst_value) != len(set(hashable(inst_value)))
	issue	= ValidateError("uniqueItems", "items :{} is not unique".format(inst_value)) if ret else None
	context.completed(issue)	
	return []

		
