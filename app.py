from flask import Flask, request, send_from_directory, render_template
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

@app.route('/venda', methods=['POST'])
def add_venda():

@app.route('/relatorio', methods=['GET'])
def get_vendas():

@app.route('/estoque', methods=['GET'])
def get_estoque():
