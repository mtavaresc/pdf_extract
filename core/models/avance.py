from dataclasses import dataclass
from datetime import date


@dataclass
class Record:
    loja: str = None
    emissao: date = None
    vencim: date = None
    renegoc: str = None
    atr: int = None
    agente: str = None
    tipo: str = None
    ep: str = None
    documento: str = None
    parc: str = None
    tipo2: str = None
    nominal: float = None
    atual_multa: float = None
    atual_juros: float = None
    atual_desconto: float = None
    atual_devido: float = None
    pagamento_multa: float = None
    pagamento_juros: float = None
    pagamento_desconto: float = None
    pagamento_pago: float = None
    pagamento: date = None
    atraso: str = None
    tipo_doc: str = None
    desconto: float = None
    multa: float = None
    juros: float = None
    operador: str = None
    complemento: str = None
    plano_contas: str = None
    observacao: str = None
