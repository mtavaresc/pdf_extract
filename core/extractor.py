import os.path
from dataclasses import dataclass
from typing import AnyStr
from typing import ClassVar
from typing import List

import numpy as np
import pandas as pd
import tabula as tb

from core import utils
from core.model import Record


@dataclass(frozen=True)
class Extractor:
    destination: ClassVar[AnyStr] = os.path.join("static", "out")
    file: AnyStr

    def execute(self):
        tables = tb.read_pdf(self.file, pages="all")

        records: List[Record] = []
        page = 0
        for table in tables:
            page += 1

            # Rename columns
            table.rename(
                {
                    "Data Histórico Custo/Receita": "Data",
                    "Recebimentos": "Histórico",
                    "Unnamed: 0": "Custo/Receita",
                    "Unnamed: 1": "Recebimentos",
                },
                axis=1,
                inplace=True,
            )

            # Delete columns before 'Saldo'
            try:
                table.drop("Unnamed: 2", inplace=True, axis=1)
            except KeyError:
                pass
            try:
                table.drop("Unnamed: 3", inplace=True, axis=1)
            except KeyError:
                pass

            table["Nota/Série/Parc. Parceiro"] = np.nan
            table["Vencimento"] = np.nan
            table["Valor Título"] = np.nan
            table["Vlr. Recebido"] = np.nan
            table["Vlr. Pago"] = np.nan

            # Moving column 'Saldo' to the ending
            try:
                last_column = table.pop("Saldo")
            except Exception as e:
                print(format(e))
                continue
            table.insert(table.columns.__len__(), "Saldo", last_column)

            if page == 1:
                # Deleting the top 3 rows
                table = table.iloc[3:, :]
            else:
                table = table.iloc[1:, :]

            table_list = [row for index, row in table.iterrows()]
            for index, row in enumerate(table_list):
                try:
                    cells = row.get("Data").split()
                except Exception as e:
                    print(format(e))
                    continue
                try:
                    idx = cells.index([i for i in cells if utils.parse_int(i)][0])
                except Exception as e:
                    print(format(e))
                    continue
                try:
                    data = utils.parse_date(cells[0])
                    past = False
                except ValueError:
                    past = True
                    data = row.get("Data").split()

                del cells[0]
                recebimentos = (
                    utils.parse_float(row.get("Histórico"))
                    if pd.isna(row.get("Recebimentos"))
                    else utils.parse_float(row.get("Recebimentos"))
                )
                pagamentos = utils.parse_float(row.get("Pagamentos"))
                custo_receita = (
                    " ".join(cells[idx: len(cells)])
                    if pd.isna(row.get("Custo/Receita"))
                    else row.get("Custo/Receita")
                )
                historico = " ".join(cells[:idx])
                saldo = utils.parse_float(row.get("Saldo"))

                # print(page, data)
                if past:
                    records[-1].nota = data[0]
                    del data[0]
                    records[-1].serie = utils.parse_int(data[0])
                    del data[0]
                    records[-1].parc = utils.parse_int(data[0])
                    del data[0]
                    records[-1].valor_titulo = (
                        utils.parse_float(data[-1])
                        if utils.parse_float(data[-1])
                        else pagamentos
                    )
                    del data[-1]
                    try:
                        records[-1].vencimento = utils.parse_date(data[-1])
                        del data[-1]
                    except ValueError:
                        records[-1].vencimento = records[-1].data

                    records[-1].parceiro = " ".join(data)
                    records[-1].valor_pago = pagamentos
                else:
                    records.append(
                        Record(
                            data=data,
                            recebimentos=recebimentos,
                            pagamentos=pagamentos,
                            custo_receita=custo_receita,
                            historico=historico,
                            saldo=saldo,
                        )
                    )
            # pd.DataFrame(records).to_csv(file.replace("data", "out").replace(".pdf", f"_{page}.csv"))

        out_file_xlsx = os.path.join(self.destination, "download.xlsx")
        pd.DataFrame(records).to_excel(out_file_xlsx)
        return out_file_xlsx
