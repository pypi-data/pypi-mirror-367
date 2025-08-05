from pathlib import Path

import numpy as np

from visdata import Table, object_vars_str


def get_expected(name: str) -> Path:
    return Path(__file__).parent / "expected_outputs" / name


def get_example_table(
    n_rows=5, n_cols=5, headings=True, named_rows=False, caption=False, numpy=False
):
    data = [[i + j * n_cols for i in range(n_cols)] for j in range(n_rows)]
    if numpy:
        data = np.array(data)

    column_labels = [f"a{i}" for i in range(n_cols)] if headings else None
    row_labels = [f"A{i}" for i in range(n_rows)] if named_rows else None
    description = "Some important values" if caption else None

    return Table(
        data,
        description=description,
        column_labels=column_labels,
        row_labels=row_labels,
    )


def test_table():
    table = get_example_table(
        n_rows=5, n_cols=5, headings=True, named_rows=True, caption=True, numpy=True
    )

    formatter = "5.2f"

    base = table.output("base", formatter=formatter)
    csv = table.csv(formatter=formatter)
    latex = table.latex(formatter=formatter)

    assert base == get_expected("test_table_base.txt").read_text()
    assert csv == get_expected("test_table_csv.txt").read_text()
    assert latex == get_expected("test_table_latex.txt").read_text()
