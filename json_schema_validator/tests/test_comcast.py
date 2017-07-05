import json
import cProfile
from logging import basicConfig, getLogger, WARN

from json_schema_validator.ref_resolver	import RefResolverFileUTF8
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
logger.setLevel(WARN)
basicConfig(format='["%(asctime)-15s", "%(levelname)s", [%(message)s]]')




TOP = 'D:\\files\\code\\json\\comcast'
TOP1 = TOP + "/"
TOP2 = TOP + "\\"


class RefResolverFunny(RefResolverFileUTF8): #RefResolverURL
	def read(self, name):
		name_ = TOP2  + name if ':' not in name else name


		logger.info('{"opening file": "%s", "file":"%s"}', name, name_)
		return super(RefResolverFunny, self).read(name_)


		


def test(json_file, json_schema):
	return Schema.from_file(json_schema, RefResolverFunny).validate(json_file, raise_if_fail = True)

def test_pair(json_file, json_schema):
	print "\n\n\n"
	print "*" * 120
	print "test"
	try:
		print "\topen", json_file
		with open(json_file) as fh:
			jf	= json.loads(fh.read())
		print "\topen", json_schema
		
		print "\ttest"			
		test(jf, json_schema)
		print "success"
	except Exception ,e:
		import traceback
		print "\tfail", e
		print traceback.format_exc()

		
def main():
	test_pair(
		TOP2 + r'sample_request_CC_SSNET_MC_TRC_GP_EGIS_COE.json',
		TOP2 + r'request_CC_SSNET_MC_TRC_GP_EGIS_COE.json'
	)
	test_pair(
		TOP2 + r'sample_request_CC_SSNET_OTDR_TRC_GP_EGIS_COE.json',
		TOP2 + r'request_CC_SSNET_OTDR_TRC_GP_EGIS_COE.json'
	)
	test_pair(
		TOP2 + r'sample_response.json',
		TOP2 + r'response_schema.json'
	)
	test_pair(
		TOP2 + r'sample_response2.json',
		TOP2 + r'response_schema_trace_up_html.json'
	)
	test_pair(
		TOP2 + r'sample_response3.json',
		TOP2 + r'response_schema.json'
	)
	
	test_pair(
		TOP2 + r'sample_response4.json',
		TOP2 + r'response_schema.json'
	)

	test_pair(
		TOP2 + r'response_schema.json',
		r'D:\files\code\python\json_schema_validator\schemas\schema.json'
	)
		
		
if __name__ == "__main__":	
	if 0:
		cProfile.run("main()")
	else:
		main()

	

