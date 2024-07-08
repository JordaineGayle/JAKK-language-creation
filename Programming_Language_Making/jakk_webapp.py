from flask import Flask, request, jsonify, render_template
from Programming_Language_Making.project_lexer_and_parser import main

app = Flask(__name__)


@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        return str(e)


@app.route('/parse', methods=['POST'])
def parse_expression():
    data = request.get_json()
    input_code = data.get('expression')

    if not input_code:
        return jsonify({'error': 'No expression provided'}), 400

    output, result = main(input_code)  # Call the main function

    return jsonify({
        'output': output,
        'result': str(result)
    })


if __name__ == '__main__':
    app.run(debug=True)
