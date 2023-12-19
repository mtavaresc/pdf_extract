from dataclasses import dataclass
from pathlib import Path
from typing import AnyStr
from typing import ClassVar
from typing import List

import pandas as pd
from xlrd import open_workbook
from xlrd.xldate import xldate_as_datetime

from core import utils
from core.models.avance import Record


@dataclass(frozen=True)
class Extractor:
    destination: ClassVar = Path("static", "out")
    file: AnyStr

    def execute(self):
        book = open_workbook(self.file)
        sheet = book.sheet_by_index(0)

        records: List[Record] = []
        for rx in range(8, sheet.nrows):
            row = sheet.row(rx)
            if not (
                utils.parse_int(row[0].value)
                or row[0].ctype == 3
                or row[0].value == "Plano de Contas:"
            ):
                continue
            if row[0].value == "Plano de Contas:":
                records[-1].plano_contas = row[3].value
                records[-1].observacao = row[16].value
                continue
            elif row[0].ctype == 3:
                records[-1].pagamento = xldate_as_datetime(row[0].value, datemode=0).date()
                records[-1].atraso = row[3].value
                records[-1].tipo_doc = row[6].value
                records[-1].desconto = utils.parse_float(row[11].value)
                records[-1].multa = utils.parse_float(row[13].value)
                records[-1].juros = utils.parse_float(row[16].value)
                records[-1].operador = row[22].value
                records[-1].complemento = row[29].value
                continue
            records.append(
                Record(
                    loja=row[0].value,
                    emissao=xldate_as_datetime(row[1].value, datemode=0).date(),
                    vencim=xldate_as_datetime(row[4].value, datemode=0).date(),
                    renegoc=row[7].value,
                    atr=utils.parse_int(row[9].value),
                    agente=row[10].value,
                    tipo=row[16].value,
                    ep=row[18].value,
                    documento=row[19].value,
                    parc=row[21].value,
                    tipo2=row[22].value,
                    nominal=utils.parse_float(row[24].value),
                    atual_multa=utils.parse_float(row[25].value),
                    atual_juros=utils.parse_float(row[27].value),
                    atual_desconto=utils.parse_float(row[30].value),
                    atual_devido=utils.parse_float(row[31].value),
                    pagamento_multa=utils.parse_float(row[32].value),
                    pagamento_juros=utils.parse_float(row[33].value),
                    pagamento_desconto=utils.parse_float(row[35].value),
                    pagamento_pago=utils.parse_float(row[38].value),
                ),
            )

        out_file_xlsx = Path(self.destination, "download.xlsx")
        pd.DataFrame(records).to_excel(out_file_xlsx)
        return out_file_xlsx
