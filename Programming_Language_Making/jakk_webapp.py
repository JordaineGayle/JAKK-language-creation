from flask import Flask, request, render_template, jsonify
from Programming_Language_Making.ai_helper import generate_ai_explanation
from Programming_Language_Making.project_lexer_and_parser import main

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/jakk', methods=['POST'])
def jakk():
    input_code = request.form.get('input_code')
    console_output, final_result = main(input_code)

    ai_explanation = generate_ai_explanation(console_output)

    return jsonify(console_output_str=console_output,
                   final_result=str(final_result),
                   ai_explanation_str=ai_explanation)


if __name__ == '__main__':
    app.run(debug=True)
