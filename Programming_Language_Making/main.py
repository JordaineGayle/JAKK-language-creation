import lexer

while True:
    text = input('basic > ')
    result, error = lexer.run('<stdin>', text)  # <stdin> is a placeholder

    if error:
        print(error.as_string())
    else:
        print(result)
