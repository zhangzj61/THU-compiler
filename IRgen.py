from astgen import AstGen
import astunparse
import ast

class CodeTransformer(ast.NodeTransformer):
    def visit_Name(self, node):
        self.generic_visit(node)
        return node

if __name__ == "__main__":

    in_file = 'funclib.pye'
    out_ast = 'module.ast'
    out_param = 'param.json'
    params = ['_param_', '_ext_', '_func_', '_fields_', '_basic_']

    astgen = AstGen()
    astgen.readInFile(in_file=in_file, params=params)
    astgen.outParam(out_file=out_param)
    r_node = astgen.outAst(out_file=out_ast)
    transformer = CodeTransformer()
    r_node = transformer.visit(r_node)
    print(astunparse.unparse(r_node))