import ply.lex as lex

tokens = (
    'VAR', 'LAMBDA', 'DOT', 'LPAREN', 'RPAREN'
)

t_VAR = r'[a-z]'
t_LAMBDA = r'#'
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

# Example usage
data = "#x.#y.xy"
lexer.input(data)
for tok in lexer:
    print(tok)
