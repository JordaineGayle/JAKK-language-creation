# Reference: https://www.youtube.com/watch?v=Eythq9848Fg&list=PLZQftyCk7_SdoVexSmwy_tBgs7P0b97yD&ab_channel=CodePulse

###########
# CONSTANTS
###########

DIGITS = '0123456789'


###########
# ERROR HANDLING
###########

class Error:
    def __init__(self, errorName, details):
        self.errorName = errorName
        self.details = details

    def as_string(self):
        result = f'{self.errorName}: {self.details}'
        return result


class IllegalCharacterError(Error):
    def __init__(self, details):
        super().__init__('Illegal Character', details)


###########
# TOKEN
###########
# Token is a simple object which has a type and optionally a value
###########

# define constants for the few token types
TT_INT = 'TT_INT'
TT_FLOAT = 'TT_FLOAT'
TT_PLUS = 'TT_PLUS'
TT_MINUS = 'TT_MINUS'
TT_MUL = 'TT_MUL'
TT_DIV = 'TT_DIV'
TT_OPBRACKET = 'TT_OPBRACKET'
TT_CLBRACKET = 'TT_CLBRACKET'


class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value

    def __repr__(self):
        if self.value: return f'{self.type}:{self.value}'
        return f'{self.type}'


###########
# LEXER
###########

class Lexer:
    # begin the lex
    def __init__(self, text):
        self.text = text
        self.pos = -1  # to keep track of the current position
        self.currentCharacter = None
        self.advance()  # to immediately begin the lexer process

    # to advance to the next character in the code
    def advance(self):
        self.pos += 1
        self.currentCharacter = self.text[self.pos] if self.pos < len(self.text) else None

    # make tokens message
    def make_tokens(self):
        tokens = []

        while self.currentCharacter is not None:
            if self.currentCharacter in '\t':
                self.advance()
            elif self.currentCharacter in DIGITS:
                tokens.append(self.make_number())
            elif self.currentCharacter == '+':
                tokens.append(Token(TT_PLUS))
                self.advance()
            elif self.currentCharacter == '-':
                tokens.append(Token(TT_MINUS))
                self.advance()
            elif self.currentCharacter == '*':
                tokens.append(Token(TT_MUL))
                self.advance()
            elif self.currentCharacter == '/':
                tokens.append(Token(TT_DIV))
                self.advance()
            elif self.currentCharacter == '(':
                tokens.append(Token(TT_OPBRACKET))
                self.advance()
            elif self.currentCharacter == ')':
                tokens.append(Token(TT_CLBRACKET))
                self.advance()
            else:
                # return some error
                char = self.currentCharacter
                self.advance()
                return [], IllegalCharacterError("'" + char + "'")

        return tokens, None

    def make_number(self):
        num_str = ''
        dot_count = 0

        while self.currentCharacter is not None and self.currentCharacter in DIGITS + '.':
            if self.currentCharacter == ".":
                if dot_count == 1:
                    break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.currentCharacter
            self.advance()

        if dot_count == 0:
            return Token(TT_INT, int(num_str))
        else:
            return Token(TT_FLOAT, float(num_str))


###########
# RUN
###########

def run(text):
    # make a new lexer to pass in the text to get the tokens out of it
    lexer = Lexer(text)
    tokens, error = lexer.make_tokens()
    return tokens, error
