import ply.yacc as yacc


class LambdaNode:
    def __init__(self, var, body):
        self.var = var
        self.body = body

    def __repr__(self):
        return f'(# {self.var} . {self.body})'


class VarNode:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name


class AppNode:
    def __init__(self, func, arg):
        self.func = func
        self.arg = arg

    def __repr__(self):
        return f'({self.func} {self.arg})'


def p_expr_var(p):
    """expr : VAR"""
    p[0] = VarNode(p[1])


def p_expr_lambda(p):
    """expr : LAMBDA VAR DOT expr"""
    p[0] = LambdaNode(p[2], p[4])


def p_expr_app(p):
    """expr : expr expr"""
    p[0] = AppNode(p[1], p[2])


def p_expr_paren(p):
    """expr : LPAREN expr RPAREN"""
    p[0] = p[2]


def p_error():
    print("Syntax error in input!")


parser = yacc.yacc()

# Example usage
data = "#x.#y.xy"
result = parser.parse(data)
print(result)
