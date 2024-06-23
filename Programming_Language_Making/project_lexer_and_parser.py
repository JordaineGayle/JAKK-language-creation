# Import the PLY library for lexical analysis and parsing
import ply.lex as lex
import ply.yacc as yacc

#############################
# LEXER
#############################

# Define tokens that the lexer will recognize
tokens = (
    'VAR', 'LAMBDA', 'DOT', 'LPAREN', 'RPAREN'
)

# Regular expression rules for simple tokens
t_VAR = r'[a-z]'  # Single lowercase letter
t_LAMBDA = r'\#'  # The hashtag symbol used instead of the lambda symbol
t_DOT = r'\.'  # Dot character
t_LPAREN = r'\('  # Left parenthesis
t_RPAREN = r'\)'  # Right parenthesis
t_ignore = ' \t'  # A string containing ignored characters (spaces and tabs)


# Rule for handling newlines
def t_newline(t):
    r"""\n+"""
    t.lexer.lineno += len(t.value)


# Error handling rule for illegal characters
def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)


# Build the lexer
lexer = lex.lex()


#############################
# PARSER
#############################

# Define the nodes for the abstract syntax tree (AST)
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


# Function Application
class AppNode:
    def __init__(self, func, arg):
        self.func = func
        self.arg = arg

    def __repr__(self):
        return f'({self.func} {self.arg})'


# Function Abstraction
class AbsNode:
    def __init__(self, var, body):
        self.var = var
        self.body = body

    def __repr__(self):
        return f'(λ {self.var} . {self.body})'


#############################
# GRAMMAR RULES
#############################
def p_expr_var(p):
    """expr : VAR"""
    p[0] = VarNode(p[1])


# def p_expr_lambda(p):
#     """expr : LAMBDA VAR DOT expr"""
#     p[0] = LambdaNode(p[2], p[4])


def p_expr_abs(p):
    """expr : LAMBDA VAR DOT expr"""
    p[0] = AbsNode(p[2], p[4])


def p_expr_app(p):
    """expr : expr expr"""
    p[0] = AppNode(p[1], p[2])


def p_expr_paren(p):
    """expr : LPAREN expr RPAREN"""
    p[0] = p[2]


# Error rule for syntax errors
def p_error(p):
    print("Syntax error in input!")


# Build the parser
parser = yacc.yacc()


#############################
# INTERPRETER
#############################

# Function to reduce expressions
def reduce(expr, env=None):
    if env is None:
        env = {}

    if isinstance(expr, VarNode):
        return env.get(expr.name, expr)  # Lookup variable in the environment

    if isinstance(expr, LambdaNode) or isinstance(expr, AbsNode):
        return expr  # Return lambda expressions as is

    if isinstance(expr, AppNode):
        func = reduce(expr.func, env)  # Reduce function part
        arg = reduce(expr.arg, env)  # Reduce argument part
        if isinstance(func, LambdaNode) or isinstance(expr, AbsNode):
            new_env = env.copy()  # Create a new environment for the lambda
            new_env[func.var] = arg  # Bind the lambda's variable to the argument
            return reduce(func.body, new_env)  # Reduce the body with the new environment
        else:
            return AppNode(func, arg)  # If not a lambda, return as an application

    return expr  # Return the expression if no reduction is possible


#############################
# RUN
#############################

# Main function to run the interpreter
def main():
    while True:
        try:
            data = input("\nEnter expression: ")
            if not data:
                continue
            result = parser.parse(data)  # Parse the input data
            print("Initial expression:", result)
            while True:
                new_result = reduce(result)  # Reduce the expression step by step
                if new_result == result:  # If no more reductions, break
                    break
                result = new_result
                print("Reduced to:", result)
            print("Normal form:", result)  # Print the final reduced form
        except EOFError:
            break  # Exit on EOF (Ctrl+D or Ctrl+Z)


# If the script is run directly, execute the main function
if __name__ == "__main__":
    main()
