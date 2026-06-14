# Backend MVC - Loja de Tecidos

API em Flask seguindo padrão MVC, com rotas para vendas, relatório e estoque de tecidos.

## Estrutura do projeto

- `app.py` - controlador principal e rotas
- `model/` - modelos SQLAlchemy (Vendedor, Tecido, Venda, ItemVenda)
- `view/` - respostas de sucesso e erro em JSON
- `database/db.sqlite3` - banco de dados SQLite local

## Dependências

Instale as dependências com:

```bash
pip install -r requirements.txt
```

## Executando localmente

Para iniciar a API:

```bash
python app.py
```

A aplicação ficará disponível em:

```text
http://localhost:5000
```

## Rotas disponíveis

### `GET /estoque`
Retorna os tecidos em estoque com quantidade em metros.

Exemplo de resposta:

```json
[
  {
    "id": 1,
    "nome": "Algodão",
    "quantidade_metros": 100.0
  },
  {
    "id": 2,
    "nome": "Poliéster",
    "quantidade_metros": 150.0
  }
]
```

### `GET /relatorio`
Retorna todas as vendas registradas com seus itens, ordenadas da mais recente para a mais antiga.

Exemplo de resposta:

```json
[
  {
    "id": 1,
    "vendedor_id": 1,
    "data_venda": "2026-06-14T12:00:00",
    "itens": [
      {
        "id": 1,
        "venda_id": 1,
        "tecido_id": 1,
        "tecido_nome": "Algodão",
        "metragem_vendida": 5.0
      }
    ]
  }
]
```

### `POST /venda`
Registra uma venda com múltiplos itens e atualiza o estoque automaticamente.

Corpo JSON esperado:

```json
{
  "vendedor_id": 1,
  "itens": [
    {
      "tecido_id": 1,
      "metragem_vendida": 5.0
    },
    {
      "tecido_id": 2,
      "metragem_vendida": 3.5
    }
  ]
}
```

Exemplo de resposta de sucesso:

```json
{
  "id": 1,
  "vendedor_id": 1,
  "data_venda": "2026-06-14T12:00:00",
  "itens": [
    {
      "id": 1,
      "venda_id": 1,
      "tecido_id": 1,
      "tecido_nome": "Algodão",
      "metragem_vendida": 5.0
    }
  ]
}
```

## Comportamento inicial

Ao iniciar a aplicação pela primeira vez, o sistema cria automaticamente:

**Vendedores:**
- João Silva
- Maria Santos

**Tecidos:**
- Algodão (100m)
- Poliéster (150m)
- Seda (50m)

## Testando as rotas

Use ferramentas como `curl`, Insomnia, Postman para testar:

```bash
curl http://localhost:5000/estoque

curl http://localhost:5000/relatorio

curl -X POST http://localhost:5000/venda \
  -H "Content-Type: application/json" \
  -d '{
    "vendedor_id": 1,
    "itens": [{"tecido_id": 1, "metragem_vendida": 5.0}]
  }'
```

## Schema do banco de dados

- **vendedores**: id, nome
- **tecidos**: id, nome, quantidade_metros
- **vendas**: id, vendedor_id, data_venda
- **itens_venda**: id, venda_id, tecido_id, metragem_vendida

## Validações

- Verificação de estoque antes da venda (validação em banco com TRIGGER)
- Atualização automática de estoque após venda registrada
- Validação de vendedor e tecido existentes
- Validação de metragem positiva