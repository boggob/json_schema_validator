from logging		import getLogger

from .exception		import ValidateException, ValidateError
from .utils			import dumps_safe

logger = getLogger('json_schema_validator.context')
debug, info, warning, error = logger.debug, logger.info, logger.warning, logger.error


class Context(object):
	def __init__(self, parent, checker = (None, None, None, None), frame = None):
		type_, validation, schema_value, inst_value	= checker

		self.parent			= parent
		self.children		= []
		self.type			= type_			#if type_		is None else getattr(parent, "type", None)
		self.validation		= validation	#if validation	is None else getattr(parent, "validation", None)
		self.schema_value	= schema_value	if schema_value	is not None else getattr(parent, "schema_value", None)
		self.inst_value		= inst_value	if inst_value	is not None else getattr(parent, "inst_value", None)
		self.id				= parent.id		if parent		else ""
		self.frame			= frame or (parent.frame if parent		else "")

		self.failed			= 0
		self.issues			= []
		self.depth_			= parent.depth + 1 if parent else 0
		self.complete		= False
		self.leaves_		= None
		self.roots_			= None

		if parent:
			parent.leaves_	= None
			parent.children.append(self)

	
	def set_id(self, id_):
		self.id = id_
		stack = list(self.children)
		while stack:
			c = stack.pop()
			stack.extend(c.children)
			c.id = id_
			
	@property
	def children_failed(self):
		return [c for c in self.children if c.failed]


	@property
	def leaves(self):
		if self.leaves_ is None:
			self.leaves_	= set()

			stack	= list(self.children)
			while stack:
				c = stack.pop()

				if not c.children:
					self.leaves_.add(c)
				else:
					stack.extend( c.children )
		return self.leaves_

	@property
	def roots(self):
		if self.roots_ is None:
			self.roots_	= set()
			parents = [self]
			while parents:
				c = parents.pop()

				if c.parent is not None:
					parents.append(c.parent)
				else:
					self.roots_.add(c)


		return self.roots_

	@property
	def depth(self):
		return self.depth_



	def completed(self, issue, force = False):

		if issue:
			self.issues.append(issue)

		if issue or force:
			top		= None
			stack	= [self]
			while stack:
				curr = stack.pop()

				#print "\t&&", curr, curr.validation, force
				if not callable(curr.validation):
					curr.complete	= True
					curr.failed		+= 1 if bool(curr.issues or any(c.failed for c in curr.children)) else 0
				else:
					curr.complete, issues_ = curr.validation(curr)

					if curr.complete and issues_:
						curr.failed	+= 1
						curr.issues.append( ValidateError(curr.type, "sub validations have failed") )

				if curr.complete:
					#print "\t#*", repr(self)
					if curr.parent:
						stack.append(curr.parent)
					elif not curr.parent:
						top = curr
						break


			if top and top.failed:
				failures = []
				stack = [top]
				while stack:
					curr = stack.pop()

					if curr.failed and curr.issues and not curr.children_failed:
						failures.append(curr)

					if curr.failed:
						stack.extend(curr.children)

				failure_	= sorted(failures, key = lambda a: a.depth, reverse = True)
					
				raise ValidateException(top, failure_)



	@staticmethod
	def all_fail(curr):
		comp	= [c for c in curr.children if c.complete]
		fail	= [c for c in curr.children if c.failed]
		fail	= [] if len(fail) < len(curr.children) else fail


		return len(comp) == len(curr.children), fail

	@staticmethod
	def any_fail(curr):
		comp	= [c for c in curr.children if c.complete]
		fail	= [c for c in curr.children if c.failed]


		return len(comp) == len(curr.children), fail

	@staticmethod
	def one_pass(curr):
		comp	= [c for c in curr.children if c.complete]
		fail1	= [c for c in curr.children if c.failed]
		passed	= [c for c in curr.children if not c.failed]



		fail	= (
						fail1	if len(fail1) + 1 != len(curr.children) and (fail1 and not passed) else
						passed	if len(passed)  != 1 else
						[]
				  )

		return len(comp) == len(curr.children), fail

	@staticmethod
	def no_pass(curr):
		comp	= [c for c in curr.children if c.complete]
		fail	= [c for c in curr.children if not c.failed]
		fail	= [] if len(fail) < len(curr.children) else fail

		return len(comp) == len(curr.children), fail


	def serialise(self, children, parents):
		return dict(
			[
				["p_id",			id(self)],
				["id",				self.id],
				["depth",			self.depth],
				["type",			self.type],
				["complete",		self.complete],
				["validation",		str(self.validation)],
				["children_failed",	len(self.children_failed)],
				["failed",			self.failed],
				["issues",			[i.serialise() for i in self.issues]],
				["schema_value",	self.schema_value],
				["schema_frame",	self.frame],
				["inst_value",		self.inst_value],
			]
			+
			(
			[
				["parent",			self.parent.serialise(False, parents)]
			]  if parents and self.parent else []
			)
			+
			(
			[
				["children",		[c.serialise(children, False) for c in self.children]]
			]  if children and self.children else []
			)
		)

	def fmt(self, indent, only=True):
		if not only:
			return dumps_safe(self.serialise(True, True))
		else:
			return dumps_safe(self.serialise(False, False))


	def __repr__(self):
		return self.fmt(1, False)


