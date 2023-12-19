import pandas as pd


def typo_zero(table):
    if pd.isnull(table.loc[1, "Recebimentos"]):
        table.drop("Recebimentos", inplace=True, axis=1)
        table.drop("Unnamed: 1", inplace=True, axis=1)
        table.rename(
            {
                "Data Histórico Custo/Receita": "Data",
                "Unnamed: 0": "Custo/Receita",
                "Unnamed: 2": "Recebimentos",
            },
            axis=1,
            inplace=True,
        )
    else:
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
    return table


def typo_one(table):
    if pd.isnull(table.loc[1, "Recebimentos"]):
        table.drop("Recebimentos", inplace=True, axis=1)
        table.rename(
            {
                "Histórico Custo/Receita": "Histórico",
                "Unnamed: 0": "Custo/Receita",
                "Unnamed: 1": "Recebimentos",
            },
            axis=1,
            inplace=True,
        )
    else:
        table.drop("Unnamed: 1", inplace=True, axis=1)
    return table


def typo_two(table):
    table["Unnamed: 0"] = table["Custo/Receita"].map(str) + " " + table["Unnamed: 0"]
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
    return table


def typo_three(table):
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
    return table


def typo_four(table):
    diff = set(table.columns).difference(
        {
            "Unnamed: 0",
            "Unnamed: 1",
            "Unnamed: 2",
            "Unnamed: 3",
            "Unnamed: 4",
            "Unnamed: 5",
            "Unnamed: 6",
            "Unnamed: 7",
        }
    )
    table.drop("Unnamed: 2", inplace=True, axis=1)
    table.drop("Unnamed: 4", inplace=True, axis=1)
    table.drop("Unnamed: 6", inplace=True, axis=1)
    table.drop("Unnamed: 7", inplace=True, axis=1)
    table.rename(
        {
            "Unnamed: 0": "Data",
            "Unnamed: 1": "Histórico",
            "Unnamed: 3": "Custo/Receita",
            "Unnamed: 5": "Pagamentos",
            list(diff)[0]: "Saldo",
        },
        axis=1,
        inplace=True,
    )
    table = table.iloc[8:-4, :]
    return table


def typo_five(table):
    table.drop("Recebimentos", inplace=True, axis=1)
    table.drop("Unnamed: 1", inplace=True, axis=1)
    table.rename(
        {
            "Unnamed: 0": "Recebimentos",
        },
        axis=1,
        inplace=True,
    )
    return table


def typo_six(table):
    table.drop("Recebimentos", inplace=True, axis=1)
    table.drop("Unnamed: 0", inplace=True, axis=1)
    table.drop("Unnamed: 2", inplace=True, axis=1)
    table.rename(
        {
            "Data Histórico": "Data",
            "Unnamed: 1": "Recebimentos",
        },
        axis=1,
        inplace=True,
    )
    return table
