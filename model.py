from dataclasses import dataclass
from datetime import date


@dataclass
class Record:
    data: date
    historico: str
    custo_receita: str
    recebimentos: float
    pagamentos: float
    nota: int = None
    serie: int = None
    parc: int = None
    parceiro: int = None
    vencimento: date = None
    valor_titulo: float = None
    valor_recebido: float = None
    valor_pago: float = None
    saldo: float = None

