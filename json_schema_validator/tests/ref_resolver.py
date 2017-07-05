if __name__ == "__main__":
	class Unbuffered(object):
	   def __init__(self, stream):
		   self.stream = stream
	   def write(self, data):
		   self.stream.write(data)
		   self.stream.flush()
	   def writelines(self, datas):
		   self.stream.writelines(datas)
		   self.stream.flush()
	   def __getattr__(self, attr):
		   return getattr(self.stream, attr)

	import sys
	a = open(r'd:\temp\out.txt', 'w')	
	sys.stdout = Unbuffered(a)
	sys.stderr = Unbuffered(a)



	import pprint
	from json_schema_validator.ref_resolver	import RefResolverFileUTF8

	class RefResolverFunny(RefResolverFileUTF8):
		def read(self, name):
			print "opening file:", name
			name = name.replace(r'http://json-schema.org/', r'D:/files/code/json/')
			return super(RefResolverFunny, self).read(name)


	ref = RefResolverFunny(r'D:\files\code\json\geojson\geojson.json')
	#pprint.pprint( ref.schema)
	
	from json_schema_validator.schema import Schema
	
	
	print Schema.from_json(ref.schema, ref).validate({ "crs" :  r'22', "type" : "Feature", "geometry" : [], "properties" : [] })
	
	#print Schema.from_json(ref.schema, ref).validate({ "crs" :  r'22', "type" : "ll" })
	
	#print Schema.from_json(ref.schema, ref).validate({ "g" :  r'22' })
	#print Schema.from_json(ref.schema, ref).validate(r'22')
	
	
	
	