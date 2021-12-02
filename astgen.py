import ast
import contextlib
import json
import re

in_file = './compiler/module.pye'
out_ast = './compiler/module.ast'
out_param = './compiler/param.json'
params = ['_param_', '_ext_', '_func_', '_fields_', '_basic_']

class AstGen:
    def __init__(self):
        pass

    def readInFile(self, in_file, params=['_param_', '_ext_', '_func_', '_fields_', '_basic_']):
        with open(in_file, 'r') as f:
            self.lines = f.readlines()
            self.content = ""
            self.to_json = []
            for line in self.lines:
                # print(line)
                if line == '\n':
                    pass
                elif line.split()[0] in params:
                    line = (line.rstrip()).split(maxsplit=1)
                    print(line)
                    para, jlist = self.stripJson(line=line, sep=';')
                    self.to_json.append({para : jlist})
                else:
                    self.content += line

    def stripJson(self, line, sep):
        para = line[0]
        jlist = (line[1:][0].rstrip(sep)).split(sep)
        cnt = 0
        for i in jlist:
            jlist[cnt] = i.strip()
            if "TH" in jlist[cnt]:
                pass
            else:
                if ':' in jlist[cnt]:
                    line = (jlist[cnt].rstrip()).split(sep=':', maxsplit=1)                   
                    _para, _jlist = self.stripJson(line=line, sep=',')
                    jlist[cnt] = {_para : _jlist}
                elif ',' in jlist[cnt]:
                    jlist[cnt] = (jlist[cnt].rstrip()).split(',')
                    cntj = 0
                    for j in jlist[cnt]:
                        jlist[cnt][cntj] = (jlist[cnt][cntj]).strip()
                        cntj += 1
                else:
                    pass                  
            cnt += 1
        print(jlist)
        return para, jlist

    def outParam(self, out_file):
        json_param = json.dumps(self.to_json, indent=2)
        with open(out_file, 'w') as f:
            f.writelines(json_param)
            f.close()

    def _is_sub_node(self, node):
        return (
            isinstance(node, ast.AST) and not isinstance(node, ast.expr_context)
        )

    def _is_leaf(self, node):
        for field in node._fields:
            attr = getattr(node, field)
            if self._is_sub_node(attr):
                return False
            elif isinstance(attr, (list, tuple)):
                for val in attr:
                    if self._is_sub_node(val):
                        return False
        else:
            return True

    def formatAst(self, node, indent='    ', _indent=0):
        if self._is_leaf(node):
            if hasattr(node, 'lineno'):
                ret = ast.dump(node)
                return ret
            else:
                return ast.dump(node)
        else:
            class state:
                indent = _indent

            @contextlib.contextmanager
            def indented():
                state.indent += 1
                yield
                state.indent -= 1

            def indentstr():
                return state.indent * indent

            def _pformat(el, _indent=0):
                return self.formatAst(el, indent=indent, _indent=_indent)

            out = type(node).__name__ + '(\n'
            with indented():
                fields = node._fields
                
                for field in fields:
                    attr = getattr(node, field)
                    if attr == []:
                        representation = '[]'
                    elif (
                            isinstance(attr, list) and
                            len(attr) == 1 and
                            isinstance(attr[0], ast.AST) and
                            self._is_leaf(attr[0])
                    ):
                        representation = '[{}]'.format(_pformat(attr[0]))
                    elif isinstance(attr, list):
                        representation = '[\n'
                        with indented():
                            for el in attr:
                                representation += '{}{},\n'.format(
                                    indentstr(), _pformat(el, state.indent),
                                )
                        representation += indentstr() + ']'
                    elif isinstance(attr, ast.AST):
                        representation = _pformat(attr, state.indent)
                    else:
                        representation = repr(attr)
                    out += '{}{}={},\n'.format(indentstr(), field, representation)
            out += indentstr() + ')'
            return out

    def outAst(self, out_file):
        a = ast.parse(self.content)
        ret = self.formatAst(a)
        with open(out_file, 'w') as f:
            f.writelines(ret)
            f.close()
        return a
    

if __name__ == "__main__":
    astgen = AstGen()
    astgen.readInFile(in_file=in_file, params=params)
    astgen.outParam(out_file=out_param)
    astgen.outAst(out_file=out_ast)