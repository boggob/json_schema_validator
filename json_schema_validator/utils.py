import collections
import re
from  json import dumps

SURROGATE_PAIR = re.compile(u'[\ud800-\udbff][\udc00-\udfff]', re.UNICODE)
def unicode_len(s):
	"""from https://stackoverflow.com/questions/12907022/python-getting-correct-string-length-when-it-contains-surrogate-pairs"""
	return len(SURROGATE_PAIR.sub('.', s)) if isinstance(s, unicode) else len(s)
	
	

def hashable(item):
	class HashableList(list):	
		def __hash__(self):
			return hash(tuple(self))
		def __eq__(self, other):
			return  len(self) == len(other) and all(a == b and type(a) == type(b)   for a,b in zip(self, other))

			
	class HashableDict(dict):	
		def __hash__(self):
			return hash(tuple(self.iteritems()))


	out = [item]
	stack  = []
	for k,v in enumerate(out):
		stack.append((out, k , v))	
	
	while stack:
		parent, key, value = stack.pop()

		if isinstance(value, bool):
			set_value(parent, key, (bool, value))
		elif isinstance(value, basestring):
			pass
		elif isinstance(value, dict):
			p = HashableDict(value.items())
			set_value(parent, key, p)
			for k,v in p.iteritems():
				stack.append((p, k , v))	
		elif hasattr(value, "__iter__"):
			p = HashableList(value)
			set_value(parent, key, p)
			for k,v in enumerate(p):
				stack.append((p, k , v))	
		
	return out[0]

	

def set_value(obj, key, value):
	obj[key]	= value
	
	
def make_multimap(it, cls=list):
	"""
	Creates a dictionary from a iterable of key-value pairs.  Values are stored
	in a list, set or other collection, ensuring that multiple values for the
	same key will be preserved.

	For example:

	``[(1,2), (2, 4), (3, 9), (1,5)]``

	 becomes

	``{1: [2,5], 2: [4], 3: [9]}``

	:param it: An iterable
	:param cls: The class-type for the defaultdict (defaults to list)
	:return: A dictionary
	"""
	items = collections.defaultdict(cls)
	func = "append" if cls is list else "add"
	for k, v in it:
		getattr(items[k], func)(v)
	return items
	
	
def assign_property_to_function(key_val_pairs):
	def real_decorator(function):	
		for property_name, property_value in key_val_pairs:
			setattr(function, property_name, property_value)
		return function
	return 	real_decorator
	

def dumps_safe(js, **kwargs):
	if "ensure_ascii" not in kwargs:
		kwargs["ensure_ascii"]	 = True
	if "encoding" not in kwargs:
		kwargs["encoding"]	 = "utf-8"
	if "sort_keys" not in kwargs:
		kwargs["sort_keys"]	 = True

		
	
	try:
		return dumps(js, **kwargs )
	except ValueError:	
		return (
				repr(js)
				.replace('None', 'null')
				.replace('True', 'true')
				.replace('False', 'false')
				.replace("u'", "'")
				.replace("'", '"')
			)
		