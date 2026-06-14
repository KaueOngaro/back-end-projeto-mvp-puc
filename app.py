from flask import Flask, request
from flasgger import Flasgger
from sqlalchemy.exc import IntegrityError

from model import Session
from model.vendedor import Vendedor
from model.tecido import Tecido
from model.venda import Venda
from model.item_venda import ItemVenda
from view.resposta_sucesso import resposta_sucesso
from view.resposta_erro import resposta_erro

app = Flask(__name__)
swagger = Flasgger(app)


@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
    return response

@app.route('/venda', methods=['OPTIONS', 'POST'])
def add_venda():
    if request.method == 'OPTIONS':
        return '', 204

    payload = request.get_json(silent=True)
    if not payload:
        return resposta_erro('JSON inválido ou corpo vazio.', 400)

    vendedor_id = payload.get('vendedor_id')
    itens = payload.get('itens')
    
    if not vendedor_id:
        return resposta_erro('O campo "vendedor_id" é obrigatório.', 400)

    if not itens or not isinstance(itens, list) or len(itens) == 0:
        return resposta_erro('O campo "itens" deve ser uma lista não vazia.', 400)

    session = Session()
    try:
        vendedor = session.query(Vendedor).filter_by(id=vendedor_id).first()
        if vendedor is None:
            return resposta_erro(f'Vendedor com ID {vendedor_id} não encontrado.', 404)

        # 1. Validação básica de formato dos itens (Sem consultar estoque no Python)
        for item in itens:
            tecido_id = item.get('tecido_id')
            metragem = item.get('metragem_vendida')

            if not tecido_id or metragem is None:
                return resposta_erro('Cada item deve ter "tecido_id" e "metragem_vendida".', 400)

            try:
                metragem = float(metragem)
            except (ValueError, TypeError):
                return resposta_erro('metragem_vendida deve ser um número.', 400)

            if metragem <= 0:
                return resposta_erro('metragem_vendida deve ser maior que zero.', 400)

        # 2. Criar o registro principal da venda
        venda = Venda(vendedor_id=vendedor_id)
        session.add(venda)
        session.flush()  # Garante a geração do ID da venda

        # 3. Inserir os itens (A Trigger do banco vai disparar automaticamente a cada insert aqui)
        for item in itens:
            tecido_id = item.get('tecido_id')
            metragem = float(item.get('metragem_vendida'))

            item_venda = ItemVenda(
                venda_id=venda.id,
                tecido_id=tecido_id,
                metragem_vendida=metragem,
            )
            session.add(item_venda)

        # Confirmar transação. Se a trigger do banco lançar um erro (ex: falta de estoque), 
        # o SQLAlchemy vai direto para o bloco except abaixo e faz o rollback.
        session.commit()
        return resposta_sucesso(venda, 201)

    except IntegrityError as err:
        session.rollback()
        print(f"ERRO DE INTEGRIDADE NO BANCO: {err}") # <-- ADICIONE ISSO
        return resposta_erro('Erro de integridade ao registrar a venda.', 500)
    except Exception as exc:
        session.rollback()
        print(f"ERRO GENÉRICO NO PYTHON/BANCO: {exc}") # <-- ADICIONE ISSO
        import traceback
        traceback.print_exc()                           # <-- ADICIONE ISSO (Mostra a linha exata)
        return resposta_erro(str(exc), 500)
    finally:
        session.close()


@app.route('/relatorio', methods=['GET'])
def get_vendas():
    """
    Retorna todas as vendas registradas com seus itens.
    ---
    tags:
      - Vendas
    responses:
      200:
        description: Lista de vendas com detalhes
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              vendedor_id:
                type: integer
              vendedor_nome:
                type: string
              data_venda:
                type: string
              itens:
                type: array
    """
    session = Session()
    try:
        vendas = session.query(Venda).order_by(Venda.data_venda.desc()).all()
        return resposta_sucesso(vendas)
    finally:
        session.close()


@app.route('/vendedores', methods=['GET'])
def get_vendedores():
    """
    Retorna a lista de vendedores cadastrados.
    ---
    tags:
      - Vendedores
    responses:
      200:
        description: Lista de vendedores
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              nome:
                type: string
    """
    session = Session()
    try:
        vendedores = session.query(Vendedor).order_by(Vendedor.nome).all()
        return resposta_sucesso(vendedores)
    finally:
        session.close()


@app.route('/estoque', methods=['GET'])
def get_estoque():
    """
    Retorna a lista de tecidos em estoque.
    ---
    tags:
      - Estoque
    responses:
      200:
        description: Lista de tecidos disponíveis
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              nome:
                type: string
              quantidade_metros:
                type: number
    """
    session = Session()
    try:
        tecidos = session.query(Tecido).order_by(Tecido.nome).all()
        return resposta_sucesso(tecidos)
    finally:
        session.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
