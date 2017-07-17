from logging		import getLogger

import codecs
from json			import loads
from re				import sub
import urllib2
try:
	from urlparse.parse import urlparse
except ImportError:
	import urlparse



from .exception		import RefResolverError
from .json_types	import Types
from .utils			import set_value


logger = getLogger('json_schema_validator.ref_resolver')
debug, info, warning, error = logger.debug, logger.info, logger.warning, logger.error



def is_absolute(url):
	return bool(urlparse.urlparse(url).netloc)



class RefResolverBase(object):

	def __init__(self, top, resolve=False):
		self.cache	= {}
		jsond		= self.file(top) if isinstance(top, basestring) else top
		self.schema	= self.resolve(jsond) if resolve else jsond


	def ref(self, name, frame = None, id_ = None, must_resolve = True):
		names	= name.strip().split("#")
		fname	= (
					names[0] if not id_ or  not is_absolute(id_) or is_absolute(names[0]) else
					names[0] if name.startswith("#") else
					id_.rsplit('/', 1)[0] + '/' + names[0]
				  )
		info('{"ref": "%s", "file":"%s", "id":"%s"}', name, fname, id_)

		if len(names) > 2:
			raise RefResolverError("Invalid reference: {}, too many # characters".format(name))
		elif len(names) == 2:
			suff	= names[1]
		else:
			suff	= ""


		if fname:
			#TODO: make threadsafe
			if fname not in self.cache:
				try:
					data	= loads(self.read(fname))
				except Exception, e:
					if must_resolve:
						raise
					else:
						data = {"$ref" : name}
						warning('{"ref": "Could not resolve filename: %s"}', fname)

				info('{"ref": "%s", "file":"%s", "contents": "%s"}', name, fname, data)
				self.cache[fname] = data
				
				#add absolute ids to cache
				self.absolute_ids_to_cache(data)
				
				
			frame	= self.cache[fname]
		elif frame is None:
			raise RefResolverError("Invalid local reference: {}, object frame is null".format(name))


		if not suff and not fname:
			value	= None
			id__	= ""
		elif not suff:
			value	= frame
			id__	= ""
		else:
			suffv = suff.split('/')
			try:
				curr = frame
				id__	= ""
				for s in suffv:
					if s:
						sr	= sub(r'\%([0-9]{2})', (lambda a: a.group(1).decode('hex')), s.replace('~1', '/').replace('~0', '~'))

						if isinstance(curr, list):
							curr = curr[int(sr)]
						else:
							id__ = self.id_cache(id__, curr.get("id"), curr)
							curr = curr[sr]
				value	= curr
			except KeyError, e:
				raise RefResolverError("Invalid local reference: {}, could not find a definition of : '{}' in: {}".format(name, e.args[0], curr), e)
			except Exception, e:
				raise RefResolverError("Invalid local reference: {},\nin scope: {},\nin frame: {}, ".format(name, curr, frame), e)

		return value, frame, id__

	def file(self, name):
		return self.ref(name)[0]


	def id_cache(self, id_exist, id_new, parent):
		out	= self.id(id_exist, id_new)
		#TODO: make threadsafe
		if out and not out.startswith("#") and not out in self.cache:
			info('{"id": "%s", "frame":"%s"}', out, parent)
			self.cache[out]	= parent
		return out

	def id(self, id_exist, id_new):

		if not isinstance(id_new, basestring):
			out = id_exist
		elif is_absolute(id_new):
			out = id_new
		else:
			id_exist1	= (
							(id_exist.rsplit('/', 1)[0] + "/") if id_exist and not id_exist.endswith('/') and id_new else
							(id_exist) if id_exist else
							""
						)

			out			= id_exist1 + id_new



		return out


	def resolve(self, start):
		self.absolute_ids_to_cache(start)

		ids = set()
		out = [start]

		stack = []
		for k, v in enumerate(out):
			stack.append( (v, v, (out, k), None ) )

		while stack:
			value, frame, parent, id_ = stack.pop()

			type_j = Types.json_type(value)
			if type_j == Types.TYPE_OBJECT:
				id_	= self.id(id_, value.get("id", ""))

				if value.get("id", "") and id_ in ids:
					warning('{"depth exceeded": "%s"}', id_)
					continue
				elif id_:
					ids.add(id_)

				ref =	value.get("$ref")
				if isinstance(ref, basestring):
					walked = set()
					while ref not in walked:
						walked.add(ref)
						deref, dframe, _	= self.ref(ref, frame, id_, must_resolve = False)

						if Types.json_type(deref) is Types.TYPE_OBJECT and deref.get("$ref"):
							ref		= deref.get("$ref")
							frame	= dframe
							id_		= self.id(id_, deref.get("id", ""))
						else:
							break

					if deref is not None:
						set_value(parent[0], parent[1], deref)

						for k, v in deref.iteritems():
							stack.append( (v, dframe, (deref, k), id_ ) )
				else:
					for k, v in value.iteritems():
						stack.append( (v, frame, (value, k), id_ ) )
			elif type_j == Types.TYPE_ARRAY:
				for k, v in enumerate(value):
					stack.append( (v, frame, (value, k), id_ ) )


		return out[0]


	def absolute_ids_to_cache(self, start):
		"""adds all absolute id's to cache"""
		
		stack = [(start, None)]

		while stack:
			value, id_ = stack.pop()

			
			type_j = Types.json_type(value)
			if type_j == Types.TYPE_OBJECT:
				id_new	= value.get("id", "")
				
				id_		= self.id_cache(id_, id_new, value)

				for v in value.itervalues():
					stack.append( (v, id_) )
			elif type_j == Types.TYPE_ARRAY:
				for v in value:
					stack.append( (v, id_) )



	def read(self, name):
		raise NotImplementedError()



class RefResolverFileUTF8(RefResolverBase):
	def read(self, name):
		try:
			with codecs.open(name, "r", "utf-8") as f:
				return f.read()
		except Exception, e:
			raise RefResolverError("Failed to open file: {}".format(name), e), None, None

class RefResolverURL(RefResolverBase):
	def read(self, name):
		try:
			obj		= urllib2.urlopen(name)
			ret		= obj.read()
			code	= obj.getcode()
			if obj.getcode() == 200:
				return ret
			else:
				raise RefResolverError("Failed to open URL: {}, exited with code: {}".format(name, code))

		except urllib2.URLError, e:
			raise RefResolverError("Failed to open URL: {}".format(name), e), None, None

