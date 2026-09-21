"""Append the evidence-backed 2026-09-14 Gold dataset task to the group demand log."""

from pathlib import Path

from docx import Document


def main() -> None:
    path = Path("docs/gestao-demandas-grupo-5.docx")
    document = Document(path)
    table = document.tables[-1]
    row = table.add_row().cells
    values = [
        "14/09/2026",
        "Grupo 5",
        "Preparação reproduzível da primeira base de previsão do ouro",
        "bases/grupo5-tratamento; bases/grupo5/gold_daily_modeling.csv; pytest (5 passed)",
        "Média",
        "Alta",
        "Concluída",
    ]
    for cell, value in zip(row, values):
        cell.text = value
    document.save(path)


if __name__ == "__main__":
    main()
