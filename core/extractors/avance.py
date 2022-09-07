import os
from dataclasses import dataclass
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
    destination: ClassVar[AnyStr] = os.path.join("static", "out")
    file: AnyStr

    def execute(self):
        book = open_workbook(self.file)
        sheet = book.sheet_by_index(0)

        records: List[Record] = []
        for rx in range(8, sheet.nrows):
            row = sheet.row(rx)
            if not (utils.parse_int(row[0].value) or row[0].ctype == 3):
                continue
            if row[0].ctype == 3:
                records[-1].pagamento = xldate_as_datetime(row[0].value, datemode=0).date()
                records[-1].atraso = row[3].value
                records[-1].tipo_doc = row[6].value
                records[-1].desconto = utils.parse_float(row[11].value)
                records[-1].multa = utils.parse_float(row[13].value)
                records[-1].juros = utils.parse_float(row[18].value)
                records[-1].operador = row[22].value
                records[-1].complemento = row[28].value
                continue
            records.append(
                Record(
                    loja=row[0].value,
                    emissao=xldate_as_datetime(row[1].value, datemode=0).date(),
                    vencim=xldate_as_datetime(row[4].value, datemode=0).date(),
                    renegoc=row[7].value,
                    atr=utils.parse_int(row[9].value),
                    agente=row[10].value,
                    tipo=row[15].value,
                    ep=row[17].value,
                    documento=row[18].value,
                    parc=row[20].value,
                    tipo2=row[21].value,
                    nominal=utils.parse_float(row[23].value),
                    atual_multa=utils.parse_float(row[24].value),
                    atual_juros=utils.parse_float(row[26].value),
                    atual_desconto=utils.parse_float(row[29].value),
                    atual_devido=utils.parse_float(row[30].value),
                    pagamento_multa=utils.parse_float(row[31].value),
                    pagamento_juros=utils.parse_float(row[32].value),
                    pagamento_desconto=utils.parse_float(row[34].value),
                    pagamento_pago=utils.parse_float(row[37].value),
                )
            )

        out_file_xlsx = os.path.join(self.destination, "download.xlsx")
        pd.DataFrame(records).to_excel(out_file_xlsx)
        return out_file_xlsx
