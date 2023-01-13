import os
import re
from dataclasses import dataclass
from typing import AnyStr
from typing import ClassVar
from typing import List

import numpy as np
import pandas as pd
import tabula as tb

from core import utils
from core.models.wtc import Record


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
            if "Data Histórico Custo/Receita" in table.columns:
                cat = 0
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
            elif "Histórico Custo/Receita" in table.columns:
                cat = 1
                table.rename(
                    {
                        "Histórico Custo/Receita": "Histórico",
                        "Unnamed: 0": "Custo/Receita",
                    },
                    axis=1,
                    inplace=True
                )
                table.drop("Unnamed: 1", inplace=True, axis=1)
            elif "Data Histórico" in table.columns:
                cat = 2
                table["Unnamed: 0"] = table['Custo/Receita'].map(str) + " " + table['Unnamed: 0']
                table.drop("Custo/Receita", inplace=True, axis=1)
                table.drop("Recebimentos", inplace=True, axis=1)
                table.rename(
                    {
                        "Data Histórico": "Data",
                        "Unnamed: 0": "Custo/Receita",
                        "Unnamed: 1": "Recebimentos",
                    },
                    axis=1,
                    inplace=True,
                )
            elif "Unnamed: 7" in table.columns:
                cat = 3
                table.drop("Unnamed: 4", inplace=True, axis=1)
                table.drop("Unnamed: 6", inplace=True, axis=1)
                table.drop("Unnamed: 7", inplace=True, axis=1)
                table.drop("Usu.:", inplace=True, axis=1)
                table.rename(
                    {
                        "Unnamed: 0": "Data",
                        "Unnamed: 1": "Histórico",
                        "Unnamed: 2": "Custo/Receita",
                        "Unnamed: 3": "Recebimentos",
                        "Unnamed: 5": "Pagamentos",
                        "4": "Saldo",
                    },
                    axis=1,
                    inplace=True,
                )
            else:
                cat = 4
                table.drop("Recebimentos", inplace=True, axis=1)
                table.drop("Unnamed: 1", inplace=True, axis=1)
                table.rename({"Unnamed: 0": "Recebimentos", }, axis=1, inplace=True)

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
                table = table.iloc[6:, :] if cat == 3 else table.iloc[1:, :]

            table_list = [row for index, row in table.iterrows()]
            for index, row in enumerate(table_list):
                try:
                    cells = row.get("Data").split()
                    if cat == 1:
                        i = row.get("Histórico")[-2:].strip()
                        cells.append(row.get("Histórico").replace(i, "").strip())
                        cells.append(i)
                        cells.append(row.get("Custo/Receita"))
                    elif cat == 2:
                        if i := re.search(r"\d+", row.get("Custo/Receita")):
                            cells.append(i.group(0))
                            cells.append(row.get("Custo/Receita").replace(f"{i}.0", "").strip())
                        else:
                            cells.append(row.get("Custo/Receita").replace(f"nan", "").strip())
                    elif cat == 3:
                        pass
                    elif cat == 4:
                        i = re.search(r"\d+", row.get("Custo/Receita")).group(0)
                        cells.append(row.get("Histórico"))
                        cells.append(i)
                        cells.append(row.get("Custo/Receita").replace(i, "").strip())
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

        out_file_xlsx = os.path.join(self.destination, "download.xlsx")
        df = pd.DataFrame(records)
        df.to_excel(out_file_xlsx)
        return out_file_xlsx
