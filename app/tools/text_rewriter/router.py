from flask import Flask, request, jsonify
from text_rewriter.core import executor

app = Flask(__name__)

@app.route('/rewrite', methods=['POST'])
def rewrite_text():
    try:
        input_data = request.json.get('input_data')
        instruction = request.json.get('instruction')
        rewritten_text = executor(input_data, instruction)
        return jsonify({"rewritten_text": rewritten_text}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)

