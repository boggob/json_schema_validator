from ..exception	import ValidateError
from ..json_types	import Types
from ..utils		import assign_property_to_function

TYPES	= Types.TYPE_NUMBER, Types.TYPE_INTEGER
	

@assign_property_to_function([["name", "maximum"], ["version", 3]])
def maximum(schema, schema_value, schema_parent, inst_value, context):
	ret		= inst_value > schema_value
	issue	= ValidateError("maximum", "value :{} is larger than allowed value: {}".format(inst_value, schema_value)) if ret else None
	context.completed(issue)	
	return []
		
@assign_property_to_function([["name", "exclusiveMaximum"], ["version", 3]])
def exclusiveMaximum(schema, schema_value, schema_parent, inst_value, context):
	ret		= schema_value and inst_value >= schema_parent.get("maximum", 0)
	issue	= ValidateError("exclusiveMaximum", "value :{} is larger than allowed value: {}".format(inst_value, schema_value)) if ret else None
	context.completed(issue)	
	return []
	
@assign_property_to_function([["name", "minimum"], ["version", 3]])
def minimum(schema, schema_value, schema_parent, inst_value, context):
	ret		= inst_value < schema_value
	issue	= ValidateError("minimum", "value :{} is smaller than allowed value: {}".format(inst_value, schema_value)) if ret else None
	context.completed(issue)	
	return []
		
@assign_property_to_function([["name", "exclusiveMinimum"], ["version", 3]])
def exclusiveMinimum(schema, schema_value, schema_parent, inst_value, context):
	ret		= schema_value and inst_value <= schema_parent.get("minimum", 0)
	issue	= ValidateError("exclusiveMinimum", "value :{} is smaller than allowed value: {}".format(inst_value, schema_value)) if ret else None
	context.completed(issue)	
	return []
	
@assign_property_to_function([["name", "multipleOf"], ["version", 3]])	
def multipleOf(schema, schema_value, schema_parent, inst_value, context):
	quotient	= inst_value / (schema_value * 1.0)
	ret		= int(quotient) != quotient
	issue	= ValidateError("multipleOf", "value :{} is not a multiple of: {}".format(inst_value, schema_value)) if ret else None
	context.completed(issue)	
	return []

