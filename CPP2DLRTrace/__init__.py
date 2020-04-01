import pycparser
from pycparser import c_parser, c_ast, parse_file, preprocess_file
from pathlib import Path


class UnprocessibleFunc(Exception):
	pass


class UnrecoverableArg(Exception):
	pass


def CPP2DRLTace(srcFile, cpp_args):
	#tf.write_text(preprocess_file(str(srcFile), cpp_args=cpp_args)
	ast = parse_file(str(srcFile), use_cpp=True, cpp_args=cpp_args)

	def processArg(arg):
		if isinstance(arg, pycparser.c_ast.Decl):
			arg = arg.type
		if isinstance(arg, pycparser.c_ast.TypeDecl):
			arg = arg.type
		if isinstance(arg, pycparser.c_ast.IdentifierType):
			return " ".join(arg.names)
		elif isinstance(arg, (pycparser.c_ast.ArrayDecl, pycparser.c_ast.PtrDecl)):
			return processArg(arg.type) + " *"
		elif isinstance(arg, (pycparser.c_ast.EllipsisParam,)):
			#raise UnprocessibleFunc(arg)
			raise UnrecoverableArg(arg)

	for d in ast:
		if isinstance(d, (pycparser.c_ast.Decl,)) and isinstance(d.type, (pycparser.c_ast.FuncDecl, pycparser.c_ast.FuncDef)):
			res = " ".join(d.type.type.type.names) + "|" + d.name + "|"

			processedArgz = []

			for arg in d.type.args.params:
				try:
					pr = processArg(arg)
					if pr is not None:
						processedArgz.append(pr)
				except UnprocessibleFunc:
					res = None
					break
				except UnrecoverableArg:
					break

			if res:
				res += "|".join(processedArgz)
				yield res


def main():
	print("\n".join(CPP2DRLTace(Path(sys.argv[0]), ["-E", r"-Iutils/fake_libc_include",] + sys.argv[1:])))
