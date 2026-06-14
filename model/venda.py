from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from model.base import Base

class Venda(Base):
    __tablename__ = 'vendas'

    id = Column(Integer, primary_key=True)
    vendedor_id = Column(Integer, ForeignKey('vendedores.id'), nullable=False)
    data_venda = Column(DateTime, nullable=False, default=datetime.utcnow)

    vendedor = relationship('Vendedor')
    itens = relationship('ItemVenda', back_populates='venda')

    def to_dict(self):
        return {
            'id': self.id,
            'vendedor_id': self.vendedor_id,
            'vendedor_nome': self.vendedor.nome if self.vendedor else None,
            'data_venda': self.data_venda.isoformat() if self.data_venda else None,
            'itens': [item.to_dict() for item in self.itens],
        }
