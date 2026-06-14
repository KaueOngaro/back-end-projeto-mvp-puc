from flask import Flask, request
from sqlalchemy.exc import IntegrityError

from model import Session
from model.vendedor import Vendedor
from model.tecido import Tecido
from model.venda import Venda
from model.item_venda import ItemVenda
from view.resposta_sucesso import resposta_sucesso
from view.resposta_erro import resposta_erro

app = Flask(__name__)


@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
    return response


def seed_initial_data():
    session = Session()
    try:
        # Criar vendedores iniciais
        if session.query(Vendedor).count() == 0:
            vendedores = [
                Vendedor(nome='João Silva'),
                Vendedor(nome='Maria Santos'),
            ]
            session.add_all(vendedores)
            session.commit()

        # Criar tecidos iniciais
        if session.query(Tecido).count() == 0:
            tecidos = [
                Tecido(nome='Algodão', quantidade_metros=100.0),
                Tecido(nome='Poliéster', quantidade_metros=150.0),
                Tecido(nome='Seda', quantidade_metros=50.0),
            ]
            session.add_all(tecidos)
            session.commit()
    except Exception:
        session.rollback()
    finally:
        session.close()


@app.before_first_request
def setup():
    seed_initial_data()


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

        # Validar todos os itens antes de processar
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

            tecido = session.query(Tecido).filter_by(id=tecido_id).first()
            if tecido is None:
                return resposta_erro(f'Tecido com ID {tecido_id} não encontrado.', 404)

            if metragem > tecido.quantidade_metros:
                return resposta_erro(
                    f'Metragem insuficiente para {tecido.nome}. Disponível: {tecido.quantidade_metros}m.',
                    400
                )

        # Criar a venda
        venda = Venda(vendedor_id=vendedor_id)
        session.add(venda)
        session.flush()  # Garante que a venda tem um ID

        # Adicionar itens e atualizar estoque
        for item in itens:
            tecido_id = item.get('tecido_id')
            metragem = float(item.get('metragem_vendida'))

            tecido = session.query(Tecido).filter_by(id=tecido_id).first()
            tecido.quantidade_metros -= metragem

            item_venda = ItemVenda(
                venda_id=venda.id,
                tecido_id=tecido_id,
                metragem_vendida=metragem,
            )
            session.add(item_venda)

        session.commit()
        return resposta_sucesso(venda, 201)

    except IntegrityError:
        session.rollback()
        return resposta_erro('Erro de integridade ao registrar a venda.', 500)
    except Exception as exc:
        session.rollback()
        return resposta_erro(str(exc), 500)
    finally:
        session.close()


@app.route('/relatorio', methods=['GET'])
def get_vendas():
    session = Session()
    try:
        vendas = session.query(Venda).order_by(Venda.data_venda.desc()).all()
        return resposta_sucesso(vendas)
    finally:
        session.close()


@app.route('/vendedores', methods=['GET'])
def get_vendedores():
    session = Session()
    try:
        vendedores = session.query(Vendedor).order_by(Vendedor.nome).all()
        return resposta_sucesso(vendedores)
    finally:
        session.close()


@app.route('/estoque', methods=['GET'])
def get_estoque():
    session = Session()
    try:
        tecidos = session.query(Tecido).order_by(Tecido.nome).all()
        return resposta_sucesso(tecidos)
    finally:
        session.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
