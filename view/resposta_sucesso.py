from flask import jsonify, make_response

def resposta_sucesso(data, status_code=200):
    response = make_response(jsonify(data.to_dict()), status_code)
    response.headers['Content-Type'] = 'application/json'
    return response