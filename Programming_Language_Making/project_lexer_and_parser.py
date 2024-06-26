# Import the PLY library for lexical analysis and parsing
import ply.lex as lex
import ply.yacc as yacc
from io import StringIO
import sys


#############################
# TOKENS
#############################

# Define tokens that the lexer will recognize
tokens = (
    'VAR', 'LAMBDA', 'DOT', 'LPAREN', 'RPAREN'
)


# Regular expression rules for simple tokens
def t_VAR(t):
    r"""[a-z]"""
    return t


def t_LAMBDA(t):
    r"""\#"""
    return t


def t_DOT(t):
    r"""\."""
    return t


def t_LPAREN(t):
    r"""\("""
    return t


def t_RPAREN(t):
    r"""\)"""
    return t


t_ignore = ' \t'  # A string containing ignored characters (spaces and tabs)


#############################
# LEXER
#############################

# Rule for handling newlines
def t_newline(t):
    r"""\n+"""
    t.lexer.lineno += len(t.value)


# Error handling rule for illegal characters
def t_error(t):
    print(f"Illegal Character or Unknown Token '{t.value[0]}'")
    t.lexer.skip(1)


# Build the lexer
lexer = lex.lex()


#############################
# PARSER
#############################

# Define the nodes for the abstract syntax tree (AST)
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
        return f'(# {self.var} . {self.body})'


#############################
# GRAMMAR RULES
#############################

def p_expr_term(p):
    """expr : term"""
    p[0] = p[1]


def p_expr_application(p):
    """expr : application"""
    p[0] = p[1]


def p_expr_abstraction(p):
    """expr : abstraction"""
    p[0] = p[1]


def p_term_var(p):
    """term : VAR"""
    p[0] = VarNode(p[1])


def p_term_paren(p):
    """term : LPAREN expr RPAREN"""
    p[0] = p[2]


def p_application(p):
    """application : expr term"""
    p[0] = AppNode(p[1], p[2])


def p_abstraction(p):
    """abstraction : LAMBDA VAR DOT expr"""
    p[0] = AbsNode(p[2], p[4])


# Error rule for syntax errors
def p_error(p):
    if p:
        print(f"Syntax error near token '{p.value}' at line {p.lineno}, position {p.lexpos}")
    else:
        print("Syntax error at EOF")


# Build the parser
parser = yacc.yacc()


#############################
# INTERPRETER
#############################

# Function to get free variables in an expression
def free_vars(expr):
    if isinstance(expr, VarNode):
        return {expr.name}
    elif isinstance(expr, AbsNode):
        return free_vars(expr.body) - {expr.var}
    elif isinstance(expr, AppNode):
        return free_vars(expr.func) | free_vars(expr.arg)
    else:
        raise TypeError(f"Unexpected expression type: {type(expr)}")


# Function to perform alpha conversion, renaming bound variables to avoid conflicts.
def alpha_convert(expr, old_var, new_var):
    if isinstance(expr, VarNode):
        return VarNode(new_var) if expr.name == old_var else expr
    elif isinstance(expr, AbsNode):
        if expr.var == old_var:
            return AbsNode(new_var, alpha_convert(expr.body, old_var, new_var))
        else:
            return AbsNode(expr.var, alpha_convert(expr.body, old_var, new_var))
    elif isinstance(expr, AppNode):
        return AppNode(alpha_convert(expr.func, old_var, new_var), alpha_convert(expr.arg, old_var, new_var))
    else:
        raise TypeError(f"Unexpected expression type: {type(expr)}")


# Function to substitute a variable in an expression with another expression, avoiding capture
def substitute(var, expr, value):
    if isinstance(expr, VarNode):
        return value if expr.name == var else expr
    elif isinstance(expr, AbsNode):
        if expr.var == var:
            return expr  # No substitution if the variable is bound in this abstraction
        elif expr.var in free_vars(value):
            new_var = expr.var + "'"
            new_body = alpha_convert(expr.body, expr.var, new_var)
            print(f"Alpha Substitution: Renaming {expr.var} to {new_var}")
            return AbsNode(new_var, substitute(var, new_body, value))
        else:
            return AbsNode(expr.var, substitute(var, expr.body, value))
    elif isinstance(expr, AppNode):
        return AppNode(substitute(var, expr.func, value), substitute(var, expr.arg, value))
    else:
        raise TypeError(f"Unexpected expression type: {type(expr)}")


# Function to perform beta reduction on expressions, reducing them step by step to their normal form.
def beta_reduce(expr):
    if isinstance(expr, VarNode):
        return expr, False
    elif isinstance(expr, AbsNode):
        reduced_body, changed = beta_reduce(expr.body)
        if changed:
            return AbsNode(expr.var, reduced_body), True
        else:
            return expr, False
    elif isinstance(expr, AppNode):
        if isinstance(expr.func, AbsNode):
            print(f"\nBeta Reduction: Applying {expr.func} to {expr.arg}")
            reduced_expr = substitute(expr.func.var, expr.func.body, expr.arg)
            print(f"\nFree Variables: {free_vars(reduced_expr)}")
            return reduced_expr, True
        else:
            reduced_func, func_changed = beta_reduce(expr.func)
            if func_changed:
                return AppNode(reduced_func, expr.arg), True
            reduced_arg, arg_changed = beta_reduce(expr.arg)
            if arg_changed:
                return AppNode(expr.func, reduced_arg), True
            return expr, False
    else:
        raise TypeError(f"\nUnexpected expression type: {type(expr)}")


# Function to check for eta reduction
def eta_reduce(expr):
    if isinstance(expr, AbsNode) and isinstance(expr.body, AppNode):
        if expr.body.arg == VarNode(expr.var) and expr.var not in free_vars(expr.body.func):
            print(f"\nEta Reduction: Reducing {expr}")
            return expr.body.func, True
    return expr, False


# Function to curry a multi-argument function
def curry(expr):
    if isinstance(expr, AbsNode):
        if isinstance(expr.body, AbsNode):
            curried_expr = AbsNode(expr.var, curry(expr.body))
            print(f"\nCurrying: {curried_expr}")
            return curried_expr
    return expr


#############################
# RUN
#############################

# Main function to run the interpreter
def main(input_code):
    import io
    import sys

    # Redirect stdout to capture print statements
    old_stdout = sys.stdout
    new_stdout = io.StringIO()
    sys.stdout = new_stdout

    try:
        if any(c.isupper() for c in input_code):  # Check for uppercase letters
            raise ValueError("Expression contains uppercase letters")
        lexer.input(input_code)  # Feed the input data to the lexer
        tokens_list = []  # Print tokens for the initial expression
        while True:
            tok = lexer.token()  # Get the next token
            if not tok:
                break  # No more tokens
            tokens_list.append(tok.type)
        print("\nTokens:", ', '.join(tokens_list))  # Print the list of tokens
        result = parser.parse(input_code)  # Parse the input data
        print("\nInitial expression:", result)

        # Curry the expression
        result = curry(result)
        print("\nCurried expression:", result)

        # Reduce the expression step by step
        while True:
            new_result, changed = beta_reduce(result)
            if not changed:  # If no more reductions, try eta reduction
                new_result, changed = eta_reduce(result)
                if not changed:
                    break
            result = new_result
            print("\nReduced to:", result)

        print("\nNormal form:", result)  # Print the final reduced form
    except ValueError as ve:
        print(f"\nInput error: {ve}")
    except SyntaxError as se:
        print(f"\nSyntax error: {se}")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        # Restore stdout
        sys.stdout = old_stdout

    # Get the console output
    console_output = new_stdout.getvalue()
    return console_output, result

# If the script is run directly, execute the main function
if __name__ == "__main__":
    main()
