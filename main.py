import os.path
from datetime import datetime
from typing import List

import numpy as np
import pandas as pd
import tabula as tb

from model import Record


def parse_int(num):
    try:
        return int(num)
    except ValueError:
        return False


def parse_float(num):
    if isinstance(num, float):
        return num
    try:
        return float(num.replace('.', '').replace(',', '.')) if num else 0
    except ValueError:
        return False


def parse_date(d):
    return datetime.strptime(d, '%d/%m/%Y').date()


def export_csv(path):
    return pd.DataFrame(records).to_csv(path.replace('pdf', 'csv'))


def export_excel(path):
    return pd.DataFrame(records).to_excel(path.replace('pdf', 'xlsx'))


if __name__ == '__main__':
    begin = datetime.now().replace(microsecond=0)

    file = 'data/FEVEREIRO.pdf'
    tables = tb.read_pdf(file, pages='all')

    records: List[Record] = []
    page = 0
    for table in tables:
        page += 1

        # Delete columns before 'Saldo'
        try:
            table.drop('Unnamed: 0', inplace=True, axis=1)
        except KeyError:
            pass
        try:
            table.drop('Unnamed: 1', inplace=True, axis=1)
        except KeyError:
            pass
        try:
            table.drop('Unnamed: 2', inplace=True, axis=1)
        except KeyError:
            pass
        try:
            table.drop('Unnamed: 3', inplace=True, axis=1)
        except KeyError:
            pass

        # Rename columns
        table.rename(
            {
                'Data Histórico Custo/Receita': 'Data',
                'Recebimentos': 'Histórico',
                'Unnamed: 0': 'Custo/Receita',
                'Unnamed: 1': 'Recebimentos',
            }, axis=1, inplace=True
        )

        table['Nota/Série/Parc. Parceiro'] = np.nan
        table['Vencimento'] = np.nan
        table['Valor Título'] = np.nan
        table['Vlr. Recebido'] = np.nan
        table['Vlr. Pago'] = np.nan

        # Moving column 'Saldo' to the ending
        try:
            last_column = table.pop('Saldo')
        except Exception as e:
            print(format(e))
            continue
        table.insert(table.columns.__len__(), 'Saldo', last_column)

        if page == 1:
            # Deleting the top 3 rows
            table = table.iloc[3:, :]
        else:
            table = table.iloc[1:, :]

        table_list = [row for index, row in table.iterrows()]
        for index, row in enumerate(table_list):
            try:
                cells = row.get('Data').split()
            except Exception as e:
                print(format(e))
                continue
            try:
                idx = cells.index([i for i in cells if parse_int(i)][0])
            except Exception as e:
                print(format(e))
                continue
            try:
                data = parse_date(cells[0])
                past = False
            except ValueError:
                past = True
                data = row.get('Data').split()

            del cells[0]
            recebimentos = parse_float(row.get('Recebimentos'))
            pagamentos = parse_float(row.get('Pagamentos'))
            custo_receita = ' '.join(cells[idx:len(cells)])
            historico = ' '.join(cells[:idx])
            saldo = parse_float(row.get('Saldo'))

            print(page, data)
            if past:
                records[-1].nota = data[0]
                del data[0]
                records[-1].serie = parse_int(data[0])
                del data[0]
                records[-1].parc = parse_int(data[0])
                del data[0]
                records[-1].valor_titulo = parse_float(data[-1]) if parse_float(data[-1]) else pagamentos
                del data[-1]
                try:
                    records[-1].vencimento = parse_date(data[-1])
                    del data[-1]
                except ValueError:
                    records[-1].vencimento = records[-1].data

                records[-1].parceiro = ' '.join(data)
                records[-1].valor_pago = pagamentos
            else:
                records.append(
                    Record(
                        data=data,
                        recebimentos=recebimentos,
                        pagamentos=pagamentos,
                        custo_receita=custo_receita,
                        historico=historico,
                        saldo=saldo
                    )
                )
        # pd.DataFrame(records).to_csv(file.replace("data", "out").replace(".pdf", f"_{page}.csv"))

    out_file_xlsx = f'out/{os.path.basename(file).replace("pdf", "xlsx")}'
    out_file_csv = f'out/{os.path.basename(file).replace("pdf", "csv")}'
    pd.DataFrame(records).to_excel(out_file_xlsx)
    pd.DataFrame(records).to_csv(out_file_csv)

    end = datetime.now().replace(microsecond=0)
    runtime = end - begin
    print('\nRuntime:', runtime, 'Avg:', runtime / page)
