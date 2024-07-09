# Import the PLY library for lexical analysis and parsing
import ply.lex as lex
import ply.yacc as yacc
import io
import sys
import string

#############################
# TOKENS
#############################

# Define lexer tokens for the language
tokens = (
    'VAR', 'ARG', 'LAMBDA', 'DOT', 'LPAREN', 'RPAREN'
)


# Regular expression rules for the tokens
def t_VAR(t):
    r"""[a-z]"""
    return t


def t_ARG(t):
    r"""[0-9]+"""
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


t_ignore = ' \t'  # to ignore characters (spaces and tabs)


#############################
# LEXER
#############################

#Handles new lines
def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")


# Error handling rule for illegal characters
def t_error(t):
    print(f"\n\nIllegal Character or Unknown Token '{t.value[0]}'")
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


class ArgNode:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return self.value


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


def p_term_arg(p):
    """term : ARG"""
    p[0] = ArgNode(p[1])


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
        print(f"\nSyntax error near token '{p.value}' at line {p.lineno}, position {p.lexpos}")
    else:
        print("\nSyntax error at EOF")


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
        # Get the free variables in the body and head of the expression
        body = free_vars(expr.body)
        head = expr.var

        # If the head variable is not the same as the body variable, treat it as free
        if head not in body:
            return body | {head}
        else:
            return body - {head}
    elif isinstance(expr, AppNode):
        return free_vars(expr.func) | free_vars(expr.arg)
    elif isinstance(expr, ArgNode):
        return set()
    else:
        raise TypeError(f"\nUnexpected expression type: {type(expr)}")


# Function to get bound variables in an expression
def bound_vars(expr, bound=None):
    if bound is None:
        bound = set()
    if isinstance(expr, VarNode):
        return bound
    elif isinstance(expr, AbsNode):
        # Only add the variable to bound if it appears in the body
        if expr.var in free_vars(expr.body):
            bound.add(expr.var)
        return bound_vars(expr.body, bound)
    elif isinstance(expr, AppNode):
        return bound_vars(expr.func, bound) | bound_vars(expr.arg, bound)
    elif isinstance(expr, ArgNode):
        return bound
    else:
        raise TypeError(f"\nUnexpected expression type: {type(expr)}")


def generate_new_var(old_var, used_vars):
    all_vars = set(string.ascii_lowercase)
    # Exclude old and used variables from the 'all variables' set
    available_vars = all_vars - {old_var} - used_vars
    if not available_vars:
        raise ValueError("No available variables for alpha conversion.")
    # Return an available variable
    return available_vars.pop()


# Function to perform alpha conversion, renaming bound variables to avoid conflicts.
def alpha_convert(expr, old_var, used_vars=None):
    if used_vars is None:
        used_vars = set()

    if isinstance(expr, VarNode):
        return VarNode(expr.name) if expr.name == old_var else expr
    elif isinstance(expr, AbsNode):
        new_var = generate_new_var(old_var, used_vars) if expr.var == old_var \
            else expr.var
        used_vars.add(new_var)
        if expr.var == old_var:
            return AbsNode(new_var, alpha_convert(expr.body, old_var, used_vars))
        else:
            return AbsNode(expr.var, alpha_convert(expr.body, old_var, used_vars))
    elif isinstance(expr, AppNode):
        return AppNode(alpha_convert(expr.func, old_var, used_vars),
                       alpha_convert(expr.arg, old_var, used_vars))
    elif isinstance(expr, ArgNode):
        return expr
    else:
        raise TypeError(f"\nUnexpected expression type: {type(expr)}")


# Function to substitute a variable in an expression with another expression,
# avoiding capture
def substitute(var, expr, replacement, used_vars=None):
    if used_vars is None:
        used_vars = set()
    if isinstance(expr, VarNode):
        return replacement if expr.name == var else expr
    elif isinstance(expr, AbsNode):
        if expr.var == var:
            return expr  # No substitution if the variable is bound in this abstraction
        elif expr.var in free_vars(replacement):
            new_var = generate_new_var(expr.var, used_vars)
            new_body = alpha_convert(expr.body, expr.var, new_var)
            print(f"\nAlpha Substitution: Renaming {expr.var} to {new_var}")
            return AbsNode(new_var, substitute(var, new_body, replacement, used_vars))
        else:
            return AbsNode(expr.var, substitute(var, expr.body, replacement, used_vars))
    elif isinstance(expr, AppNode):
        return AppNode(substitute(var, expr.func, replacement, used_vars),
                       substitute(var, expr.arg, replacement, used_vars))
    elif isinstance(expr, ArgNode):
        return expr
    else:
        raise TypeError(f"\nUnexpected expression type: {type(expr)}")


# Function to perform beta reduction on expressions,
# reducing them step by step to their normal form.
def beta_reduce(expr):
    if isinstance(expr, VarNode) or isinstance(expr, ArgNode):
        return expr, False
    elif isinstance(expr, AbsNode):
        reduced_body, changed = beta_reduce(expr.body)
        if changed:
            return AbsNode(expr.var, reduced_body), True
        else:
            return expr, False
    elif isinstance(expr, AppNode):
        if isinstance(expr.func, AbsNode):
            print(f"\nBeta Reduction: Applying {expr.arg} to {expr.func}")
            reduced_expr = substitute(expr.func.var, expr.func.body, expr.arg)
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
        if isinstance(expr.body.arg, VarNode) and expr.body.arg.name == expr.var:
            if expr.var not in free_vars(expr.body.func):
                print(f"\nEta Reduction: Reducing {expr}")
                return expr.body.func, True
    return expr, False


# Function to curry a multi-argument function
def curry(expr):
    if isinstance(expr, AbsNode):
        if isinstance(expr.body, AbsNode):
            curried_body = curry(expr.body)
            if curried_body is not expr.body:
                # If the body has been curried, create a new abstraction node
                curried_expr = AbsNode(expr.var, curried_body)
                print(f"\nCurrying: {curried_expr}")
                return curried_expr
        return expr
    return expr


# Function to construct the parse tree/ abstract syntax tree (AST)
def parse_tree_str(node):
    if isinstance(node, VarNode):
        return f"Variable('{node.name}')"
    elif isinstance(node, ArgNode):
        return f"Argument('{node.value}')"
    elif isinstance(node, AppNode):
        return f"Application({parse_tree_str(node.func)}, {parse_tree_str(node.arg)})"
    elif isinstance(node, AbsNode):
        return f"Abstraction('{node.var}', {parse_tree_str(node.body)})"
    else:
        raise TypeError(f"Unexpected node type: {type(node)}")


#############################
# RUN
#############################

# Main function to run the interpreter
def main(input_code):
    # Redirect stdout to capture print statements
    old_stdout = sys.stdout
    new_stdout = io.StringIO()
    sys.stdout = new_stdout

    result = None  # Initialize result variable

    try:
        if any(c.isupper() for c in input_code):  # Check for uppercase letters
            raise ValueError("\nExpression contains uppercase letters")

        # Parse Tree Generator
        lexer.input(input_code)  # Feed the input data to the lexer
        tokens_list = []  # Print tokens for the initial expression
        while True:
            tok = lexer.token()  # Get the next token
            if not tok:
                break  # No more tokens
            tokens_list.append(tok.type)

        print("Tokens:", ', '.join(tokens_list))  # Print the list of tokens
        result = parser.parse(input_code)  # Parse the input data
        print("\nParse Tree:")
        print(f"Start expression {input_code} -> {parse_tree_str(result)}")  # Print Parse Tree

        # Identify free and bound variables
        free = free_vars(result)
        if not free:
            print("\nFree variables: None")
        else:
            print("\nFree variables:", free)

        bound = bound_vars(result)
        if not bound:
            print("\nBound variables: None")
        else:
            print("\nBound variables:", bound)

        # Curry the expression
        result = curry(result)
        print("\nCurried expression:", result)

        # Normal Form
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
        print(f"\n\nSyntax error: {se}")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        # Restore stdout
        sys.stdout = old_stdout

    # Get the console output
    console_output = new_stdout.getvalue()
    return console_output, result

# If the script is run directly, execute the main function
# if __name__ == "__main__":
#     main()
