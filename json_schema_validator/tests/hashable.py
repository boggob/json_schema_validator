if __name__ == "__main__":

	import pprint	
	from json_schema_validator.utils	import hashable

	x =  hashable([{"A" : [1, {"3" : "4"}]}])	
	
	
	print hash(x)
	
	print {hashable([{"A" : [1, {"3" : "4"}]}]), hashable([{"A" : [1, {"3" : "4"}]}])	, hashable([{"A" : [1, {"3" : "4"}]}])	, hashable([{"A" : [1, {"3" : "4"}]}])	}

	
		
	@decorator_with_args("name", "$pissy")	
	def x(y):
		return y + 1
		
	print x, x.name	