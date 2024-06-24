# Import the PLY library for lexical analysis and parsing
import ply.lex as lex
import ply.yacc as yacc

#############################
# TOKENS
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

# Function to reduce expressions
def reduce(expr, env=None):
    if env is None:
        env = {}

    try:
        if isinstance(expr, VarNode):
            return env.get(expr.name, expr), False  # Lookup variable in the environment and indicate no change

        elif isinstance(expr, AbsNode):
            return expr, False  # Return abstraction expressions as is with no change

        elif isinstance(expr, AppNode):
            func, changed_func = reduce(expr.func, env)  # Reduce function part
            arg, changed_arg = reduce(expr.arg, env)  # Reduce argument part

            if isinstance(func, AbsNode):
                # Substitute the argument into the body of the function
                new_env = {**env, func.var: arg}
                reduced_body, changed_body = reduce(func.body, new_env)

                if changed_func or changed_arg or changed_body:
                    print(f"Applied function: ({func} {arg}) -> {reduced_body}")

                return reduced_body, True

            else:
                return AppNode(func, arg), changed_func or changed_arg

        else:
            raise TypeError(f"Unexpected expression type: {type(expr)}")

    except Exception as e:
        raise RuntimeError(f"Error in reducing expression: {e}")


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
            if any(c.isupper() for c in data):  # Check for uppercase letters
                raise ValueError("Expression contains uppercase letters")
            result = parser.parse(data)  # Parse the input data
            print("Initial expression:", result)

            # Reduce the expression step by step
            while True:
                new_result, changed = reduce(result)
                if not changed:  # If no more reductions, break
                    break
                result = new_result
                print("Reduced to:", result)

            print("Normal form:", result)  # Print the final reduced form
            print("\nTo exit, press Ctrl+D")

        except EOFError:
            break  # Exit on EOF (Ctrl+D)
        except ValueError as ve:
            print(f"Input error: {ve}")
        except SyntaxError as se:
            print(f"Syntax error: {se}")
        except Exception as e:
            print(f"Error: {e}")


# If the script is run directly, execute the main function
if __name__ == "__main__":
    main()
