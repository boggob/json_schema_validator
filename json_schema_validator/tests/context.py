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
	#sys.stdout = Unbuffered(open(r'd:\temp\out.txt', 'w'))



	import pprint	
	from json_schema_validator.context	import Context

	root = Context(None, ([None, None], Context.any_fail, None, None))
	t = []
	
	for i in range(1, 6):
		c = Context(root, ([i, None], Context.all_fail, None, None))
		for j in range(1, 5):
			d = Context(c, ([i, j], None, None, None))
			t.append(d)
	
	d.validation = Context.all_fail
	#print d
	x = Context(d, ([i, j, 1], Context.all_fail, None, None))		
	t.append(  Context(x, ([i, j, 1, 1], None, None, None))		 )
	
	for r in t:	
		print r, repr(r.parent)
	
	y = x.roots
	print "^^^", [r.type for r in x.roots]
	for r in x.roots:
		for l in r.leaves:
			print "7", l
	
	
	for r in t:	
		r.completed(1)


	print root
	
	
	