from flask import jsonify, make_response


def resposta_sucesso(data, status_code=200):
    if hasattr(data, 'to_dict'):
        body = data.to_dict()
    elif isinstance(data, list):
        body = [item.to_dict() if hasattr(item, 'to_dict') else item for item in data]
    else:
        body = data

    response = make_response(jsonify(body), status_code)
    response.headers['Content-Type'] = 'application/json'
    return response