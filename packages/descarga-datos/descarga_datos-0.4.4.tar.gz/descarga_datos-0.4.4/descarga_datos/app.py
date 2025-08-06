from descarga_datos.internals.setup_data import read_json, setup_data_by_report

import typer
import pandas as pd

app = typer.Typer()


@app.command()
def setup_data(file_data_name: str = "", report: str = "", analysis: str = "analyses.json"):
    data_to_filter = pd.read_csv(file_data_name)
    analyses_list = read_json(analysis)
    filtered_data = setup_data_by_report(data_to_filter, report, analyses_list)
    filtered_data.to_csv(file_data_name, index=False)
