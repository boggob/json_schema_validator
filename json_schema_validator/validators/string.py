from re				import compile as compile_re, IGNORECASE



try:
	import ipaddress
	def is_ipv6(instance):
		try:
			return ipaddress.ip_address(instance)
		except Exception:
			return False
	
except ImportError:
	def is_ipv6(instance):
		return True



try:
	import strict_rfc3339
	def is_datetime(instance):
		return strict_rfc3339.validate_rfc3339(instance)
	
except ImportError:
	try:
		import isodate
		def is_datetime(instance):
			return isodate.parse_datetime(instance)		
	except ImportError:
		def is_datetime(instance):
			return True


from ..exception	import ValidateError
from ..json_types	import Types
from ..utils		import assign_property_to_function, unicode_len


TYPES	= Types.TYPE_STRING,
	
@assign_property_to_function([["name", "pattern"], ["version", 3]])
def pattern(schema, schema_value, schema_parent, inst_value, context):
	comp	= compile_re(schema_value)
	ret		= not comp.search(inst_value)
	issue	= ValidateError("pattern", "Expected pattern: {}, inst_value: {}".format(schema_value, inst_value)) if ret else None
	context.completed(issue)	
	return []


	
_email		= compile_re(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")
_url		= compile_re(
				r'^(?:http|ftp)s?://' # http:// or https://
				r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
				r'localhost|' #localhost...
				r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
				r'(?::\d+)?' # optional port
				r'(?:/?|[/?]\S+)$',
			IGNORECASE
			)
_ipv4_re	= compile_re(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
_host_name_re = compile_re(r"^[A-Za-z0-9][A-Za-z0-9\.\-]{1,255}$")


def is_ipv4(instance):
	if not _ipv4_re.match(instance):
		return False
	return all(0 <= int(component) <= 255 for component in instance.split("."))

def is_host_name(instance):
	return _host_name_re.match(instance) and not any(len(c) > 63 for c in instance.split("."))

	
	

@assign_property_to_function([["name", "format"], ["version", 3]])
def format_(schema, schema_value, schema_parent, inst_value, context):
	
	if schema_value == "email":
		ret		= not _email.search(inst_value)
		issue	= ValidateError("format", "Expected: {}, inst_value: {}".format(schema_value, inst_value)) if ret else None
		context.completed(issue)	
		return []
	elif schema_value == "date-time":
		ret		= not is_datetime(inst_value)
		issue	= ValidateError("format", "Expected: {}, inst_value: {}".format(schema_value, inst_value)) if ret else None
		context.completed(issue)	
		return []	
	elif schema_value == "uri":
		ret		= not _url.search(inst_value)
		issue	= ValidateError("format", "Expected: {}, inst_value: {}".format(schema_value, inst_value)) if ret else None
		context.completed(issue)	
		return []		
	elif schema_value == "ipv4":
		ret		= not is_ipv4(inst_value)
		issue	= ValidateError("format", "Expected: {}, inst_value: {}".format(schema_value, inst_value)) if ret else None
		context.completed(issue)	
		return []		
		
	elif schema_value == "ipv6":
		ret		= not is_ipv6(inst_value)
		issue	= ValidateError("format", "Expected: {}, inst_value: {}".format(schema_value, inst_value)) if ret else None
		context.completed(issue)	
		return []		
	elif schema_value == "hostname":
		ret		= not is_host_name(inst_value)
		issue	= ValidateError("format", "Expected: {}, inst_value: {}".format(schema_value, inst_value)) if ret else None
		context.completed(issue)	
		return []		
	elif schema_value == "regex":
		ret		= not compile_re(inst_value)
		issue	= ValidateError("format", "Expected: {}, inst_value: {}".format(schema_value, inst_value)) if ret else None
		context.completed(issue)	
		return []		
		
	else:	
		context.completed(None)	
		return []
	

@assign_property_to_function([["name", "minLength"], ["version", 3]])
def minLength(schema, schema_value, schema_parent, inst_value, context):
	ret		= unicode_len(inst_value) < schema_value
	issue	= ValidateError("minLength", "length :{} is shorter than allowed length: {}".format(unicode_len(inst_value), schema_value)) if ret else None
	context.completed(issue)	
	return []


@assign_property_to_function([["name", "maxLength"], ["version", 3]])
def maxLength(schema, schema_value, schema_parent, inst_value, context):
	ret		= unicode_len(inst_value) > schema_value
	issue	= ValidateError("maxLength", "length :{} is longer than allowed length: {} for string".format(unicode_len(inst_value), schema_value)) if ret else None
	context.completed(issue)	
	return []

		