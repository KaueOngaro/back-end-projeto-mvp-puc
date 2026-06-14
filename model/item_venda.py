from sqlalchemy import Column, Integer, ForeignKey, Float
from sqlalchemy.orm import relationship
from model.base import Base

class ItemVenda(Base):
    __tablename__ = 'itens_venda'

    id = Column(Integer, primary_key=True)
    venda_id = Column(Integer, ForeignKey('vendas.id'), nullable=False)
    tecido_id = Column(Integer, ForeignKey('tecidos.id'), nullable=False)
    metragem_vendida = Column(Float, nullable=False)

    venda = relationship('Venda', back_populates='itens')
    tecido = relationship('Tecido', back_populates='itens_venda')

    def to_dict(self):
        return {
            'id': self.id,
            'venda_id': self.venda_id,
            'tecido_id': self.tecido_id,
            'tecido_nome': self.tecido.nome if self.tecido else None,
            'metragem_vendida': self.metragem_vendida,
        }
