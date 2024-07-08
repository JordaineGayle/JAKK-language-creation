from flask import Flask, request, render_template, jsonify
from Programming_Language_Making.project_lexer_and_parser import main as process_jakk

app = Flask(__name__)


@app.route('/')
def index():
    try:
        console_output_str = "<div class='console'>Waiting for compilation...</div>"
        final_result = ""
        return render_template("index.html",
                               console_output_str=console_output_str,
                               final_result=final_result)
    except Exception as e:
        return str(e)


@app.route('/jakk', methods=['POST'])
def compile_code():
    try:
        input_code = request.form['input_code']
        console_output_str, final_result = process_jakk(input_code)
        response = {
            'console_output': console_output_str,
            'final_result': final_result
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)})


if __name__ == '__main__':
    app.run(debug=True)
