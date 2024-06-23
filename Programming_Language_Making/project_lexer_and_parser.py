import ply.lex as lex
import ply.yacc as yacc

#############################

# LEXER

#############################

# Lexer definition
tokens = (
    'VAR', 'LAMBDA', 'DOT', 'LPAREN', 'RPAREN'
)

t_VAR = r'[a-zA-Z]'
t_LAMBDA = r'\#'
t_DOT = r'\.'
t_LPAREN = r'\('
t_RPAREN = r'\)'

t_ignore = ' \t'


def t_newline(t):
    r"""\n+"""
    t.lexer.lineno += len(t.value)


def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)


lexer = lex.lex()


#############################

# PARSER

#############################


# Parser definition
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


def p_error(p):
    print("Syntax error in input!")


parser = yacc.yacc()


# # Example usage
# data = "#x.#y.xy"
# result = parser.parse(data)
# print(result)


#############################

# INTERPRETER

#############################

def reduce(expr, env=None):
    if env is None:
        env = {}

    if isinstance(expr, VarNode):
        return env.get(expr.name, expr)

    if isinstance(expr, LambdaNode):
        return expr

    if isinstance(expr, AppNode):
        func = reduce(expr.func, env)
        arg = reduce(expr.arg, env)
        if isinstance(func, LambdaNode):
            new_env = env.copy()
            new_env[func.var] = arg
            return reduce(func.body, new_env)
        else:
            return AppNode(func, arg)

    return expr


# # Example usage
# data = "#x.#y.xy"
# result = parser.parse(data)
# print("Initial expression:", result)
# while True:
#     new_result = reduce(result)
#     if new_result == result:
#         break
#     result = new_result
#     print("Reduced to:", result)
# print("Normal form:", result)


#############################

# RUN

#############################


# Main function to run the interpreter
def main():
    while True:
        try:
            data = input("Enter expression: ")
            if not data:
                continue
            result = parser.parse(data)
            print("Initial expression:", result)
            while True:
                new_result = reduce(result)
                if new_result == result:
                    break
                result = new_result
                print("Reduced to:", result)
            print("Normal form:", result)
        except EOFError:
            break


if __name__ == "__main__":
    main()