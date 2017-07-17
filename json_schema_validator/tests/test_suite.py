import json
import os
import os.path

import traceback
import codecs
import cProfile
import time
from logging import basicConfig, getLogger, DEBUG as LEVEL

from json_schema_validator.ref_resolver	import RefResolverFileUTF8, RefResolverURL
from json_schema_validator.schema		import Schema

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


logger = getLogger('json_schema_validator')
logger.setLevel(LEVEL)
basicConfig(format='["%(asctime)-15s", "%(levelname)s", [%(message)s]]')






class RefResolverFunny(RefResolverFileUTF8): #RefResolverURL
	def read(self, name):
		name_ = name.replace(r'http://json-schema.org/draft-04/schema', 'D:\\files\\code\\python\\json_schema_validator\\schemas\\schema.json')
		name_ = name_.replace(r'http://localhost:1234/',  'D:\\files\\code\\json\\JSON-Schema-Test-Suite-master\\remotes\\').split('#')[0]

		logger.info('{"opening file": "%s", "file":"%s"}', name, name_)
		#raise ValueError(name)
		return super(RefResolverFunny, self).read(name_)


def all_files(path):

	for file_ in sorted(os.listdir(path)):
		file_1 = os.path.join(path, file_)
		if os.path.isdir(file_1):
			for s in all_files(file_1):
				yield s
		else:
			yield file_1



def test_(path):
	for file_ in sorted(all_files(path)):
		file_1 = os.path.join(path, file_)
		with codecs.open(file_1) as fh:
			for test in json.loads(fh.read(),encoding="utf-8"):
				#ref = RefResolverFunny(r'D:\files\code\json\geojson\geojson.json')
				print "\n" * 4
				print "*" * 120
				print "@@!", file_1, test['description'], test

				try:
					schema = Schema.from_json(test["schema"], RefResolverFunny)
				except Exception, e:
					schema = None
					for t in test["tests"]:
						print "\n" * 2
						print "*" * 120
						print file_1, t,

						print ["test failed", file_1, t, e, traceback.format_exc()]


				if schema is not None:
					print schema.schema
					for t in test["tests"]:
						print "\n" * 2
						print "*" * 120

						try:
							ret =  schema.validate(t["data"], raise_if_fail = False)
							if t["valid"] and ret or not t["valid"] and not ret:
								print ["test failed", file_1, test['description'], t, ret]
							else:
								print ["test passed", file_1, test['description'], t, "\n", ret]

						except Exception, e:
							print ["test failed", file_1, test['description'], t, e, traceback.format_exc()]


if __name__ == "__main__":
	PATH = r'D:\files\code\json\JSON-Schema-Test-Suite-master\tests\draft4'
	
	if 1:
		start = time.time()
		test_(PATH)
		print  "time taken", time.time() - start
	else:	
		cProfile.run("test_(PATH)")
	
