import re
from dataclasses import dataclass
from pathlib import Path
from typing import AnyStr
from typing import ClassVar

import numpy as np
import pandas as pd
import tabula as tb

from core import utils
from core.models.wtc import Record
from core.extractors.parser_wtc import parser_table


@dataclass(frozen=True)
class Extractor:
    destination: ClassVar = Path("static", "out")
    file: AnyStr

    def execute(self):
        global cat
        tables = tb.read_pdf(self.file, pages="all")

        records: list[Record] = []
        page = 0
        for table in tables:
            page += 1
            # Rename columns
            if "Data Histórico Custo/Receita" in table.columns:
                cat = 0
                table = parser_table.typo_zero(table)
            elif {
                "Data",
                "Histórico Custo/Receita",
                "Unnamed: 0",
                "Recebimentos",
                "Unnamed: 1",
                "Pagamentos",
                "Saldo",
            } == set(table.columns):
                cat = 1
                table = parser_table.typo_one(table)
            elif {
                "Data Histórico",
                "Custo/Receita",
                "Unnamed: 0",
                "Recebimentos",
                "Unnamed: 1",
                "Pagamentos",
                "Saldo",
            } == set(table.columns):
                cat = 2
                table = parser_table.typo_two(table)
            elif {
                "Unnamed: 0",
                "Unnamed: 1",
                "Unnamed: 2",
                "Unnamed: 3",
                "Unnamed: 4",
                "Unnamed: 5",
                "Unnamed: 6",
                "Unnamed: 7",
                "Usu.:",
                "4",
            }.issubset(table.columns):
                cat = 3
                table = parser_table.typo_three(table)
            elif {
                "Unnamed: 0",
                "Unnamed: 1",
                "Unnamed: 2",
                "Unnamed: 3",
                "Unnamed: 4",
                "Unnamed: 5",
                "Unnamed: 6",
                "Unnamed: 7",
            }.issubset(table.columns):
                cat = 4
                table = parser_table.typo_four(table)
            elif {
                "Data",
                "Histórico",
                "Custo/Receita",
                "Recebimentos",
                "Unnamed: 0",
                "Pagamentos",
                "Unnamed: 1",
                "Saldo",
            } == set(table.columns):
                cat = 5
                table = parser_table.typo_five(table)
            elif {
                "Data Histórico",
                "Custo/Receita",
                "Recebimentos",
                "Unnamed: 0",
                "Unnamed: 1",
                "Pagamentos",
                "Unnamed: 2",
                "Saldo",
            } == set(table.columns):
                cat = 6
                table = parser_table.typo_six(table)
            elif {
                "Unnamed: 0",
                "Custo/Receita",
                "Unnamed: 3",
                "Saldo",
                "Unnamed: 2",
                "Recebimentos",
                "Unnamed: 1",
                "Pagamentos",
                "Data Histórico",
            }.issubset(table.columns):
                cat = 7
                table = parser_table.typo_seven(table)
            elif {
                "Data",
                "Histórico",
                "Unnamed: 2",
                "Pagamentos",
                "Recebimentos",
                "Unnamed: 1",
                "Unnamed: 0",
                "Custo/Receita",
                "Saldo",
            } == set(table.columns):
                cat = 8
                table = parser_table.typo_eight(table)
            else:
                print(f"Page #{page} not tracked: {set(table.columns)}")

            # Delete columns before 'Saldo'
            try:
                table.drop("Unnamed: 2", inplace=True, axis=1)
            except KeyError:
                pass
            try:
                table.drop("Unnamed: 3", inplace=True, axis=1)
            except KeyError:
                pass
            try:
                table.drop("Unnamed: 4", inplace=True, axis=1)
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
            except KeyError:
                continue
            table.insert(table.columns.__len__(), "Saldo", last_column)

            if page == 1:
                # Deleting the top 3 rows
                table = table.iloc[3:, :]
            else:
                table = table.iloc[4:, :] if cat == 3 else table.iloc[1:, :]

            table_list = [row for index, row in table.iterrows()]
            for index, row in enumerate(table_list):
                try:
                    # split column "Date" to create column "History"
                    cells = row.get("Data").split()
                    if cat == 1:
                        i = row.get("Histórico")[-2:].strip()
                        cells.append(row.get("Histórico").replace(i, "").strip())
                        cells.append(i)
                        cells.append(row.get("Custo/Receita"))
                    elif cat in {2, 7}:
                        if i := re.search(r"\d+", row.get("Custo/Receita")):
                            cells.append(i.group(0))
                            cells.append(
                                row.get("Custo/Receita").replace(f"{i.group(0)}.0", "").strip(),
                            )
                        else:
                            cells.append(row.get("Custo/Receita").replace("nan", "").strip())
                    elif cat == 4:
                        if i := re.search(r"(\d+,\d+)", row.get("Custo/Receita")):
                            row["Custo/Receita"] = (
                                row.get("Custo/Receita").replace(i.group(0), "").strip()
                            )
                            row["Recebimentos"] = i.group(0)
                    elif cat in {3, 5}:
                        if i := re.search(r"\d+", row.get("Custo/Receita")):
                            cells.append(row.get("Histórico"))
                            cells.append(i.group(0))
                            cells.append(row.get("Custo/Receita").replace(i.group(0), "").strip())
                        else:
                            i = row.get("Histórico")[-2:].strip()
                            cells.append(row.get("Histórico").replace(i, "").strip())
                            cells.append(i)
                            cells.append(row.get("Custo/Receita"))
                except Exception as e:
                    print(format(e))
                    continue

                try:
                    data = utils.parse_date(cells[0])
                    past = False
                except ValueError:
                    ix = list(row.values).index(
                        [r for r in list(row.values) if not isinstance(r, str)][0]
                    )
                    data = " ".join(list(row.values)[:ix]).split()
                    past = True

                del cells[0]

                if found_int_in_cells := [i for i in cells if utils.parse_int(i)]:
                    idx = cells.index(found_int_in_cells[0])
                else:
                    idx = None

                # Setting Recebimentos
                recebimentos = (
                    utils.parse_float(row.get("Histórico"))
                    if pd.isna(row.get("Recebimentos"))
                    else utils.parse_float(row.get("Recebimentos"))
                )

                # Setting Pagamentos
                pagamentos = utils.parse_float(row.get("Pagamentos"))

                # Setting Custo/Receita
                custo_receita = (
                    " ".join(cells[idx : len(cells)])
                    if pd.isna(row.get("Custo/Receita"))
                    else row.get("Custo/Receita")
                )
                historico = " ".join(cells[:idx]) if idx else " ".join(cells)
                historico = historico if historico else row.get("Histórico")

                # Setting Saldo
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
                        utils.parse_float(data[-1]) if utils.parse_float(data[-1]) else pagamentos
                    )
                    del data[-1]
                    try:
                        records[-1].vencimento = utils.parse_date(data[-1])
                        del data[-1]
                    except ValueError:
                        records[-1].vencimento = records[-1].data
                    except IndexError:
                        records[-1].vencimento = None

                    records[-1].parceiro = " ".join(data) if data else None
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
                        ),
                    )

        out_file_xlsx = Path(self.destination, "download.xlsx")
        pd.DataFrame(records).to_excel(out_file_xlsx)
        return out_file_xlsx
