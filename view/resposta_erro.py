from flask import jsonify, make_response

def resposta_erro(error_msg, status_code=400):
    response = make_response(jsonify({"error": error_msg}), status_code)
    response.headers['Content-Type'] = 'application/json'
    return response