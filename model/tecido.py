from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from model.base import Base

class Tecido(Base):
    __tablename__ = 'tecidos'

    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    quantidade_metros = Column(Float, nullable=False)

    itens_venda = relationship('ItemVenda', back_populates='tecido')

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'quantidade_metros': self.quantidade_metros,
        }
