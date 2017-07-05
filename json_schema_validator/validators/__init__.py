import importlib


def _validators():
	vals	= [".all", ".array", ".numeric", ".object", ".string"]
	mods	= [importlib.import_module(_v, "json_schema_validator.validators") for _v in vals]
	
	return {

				t :	[
									_o
									for _n in dir(m) 
									for _o in [getattr(m, _n)]
									if hasattr(_o, "name")
								]

				for m in mods
				for t in m.TYPES
				
				
			}

VALIDATORS	= _validators()