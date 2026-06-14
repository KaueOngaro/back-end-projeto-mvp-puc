from sqlalchemy import Column, Integer, String
from model.base import Base

class Vendedor(Base):
    __tablename__ = 'vendedores'

    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False, unique=True)

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
        }
