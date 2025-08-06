import json
import pandas as pd
import warnings


def setup_data_by_report(data_to_filter, target_report, analyses_list):
    report_content = extract_report_content(target_report, analyses_list)
    filter_condition = find_filter_condition(report_content)
    return filter_date_by_condition(data_to_filter, filter_condition)


def filter_date_by_condition(data_to_filter, conditional_year):
    if conditional_year is None:
        return data_to_filter
    copy_data_to_filter = data_to_filter.copy()
    copy_data_to_filter.dropna(subset=["Fecha"], inplace=True)
    copy_data_to_filter["year"] = copy_data_to_filter["Fecha"].str.slice(7).astype(int)
    copy_data_to_filter.query("year " + conditional_year, inplace=True)
    return copy_data_to_filter.drop(columns=["year"])


def find_filter_condition(report_content):
    setup_key = "setup_data"
    if setup_key not in report_content.keys():
        return None
    return report_content[setup_key][0]["season"]


def extract_report_content(target_report, analyses_list):
    target_report_content = [
        report_content
        for report_content in analyses_list
        if report_content["report"] == target_report
    ]
    if len(target_report_content) == 0:
        raise ValueError(f"There is not report {target_report}")
    return target_report_content[0]


def _adapt_columns(file_name, destination_folder):
    extension = file_name.split(".").pop()
    if extension == "csv":
        file_path = f"{destination_folder}/{file_name}"
        file_df = pd.read_csv(file_path)
        file_df.rename(columns={"Date": "Fecha"}, inplace=True)
        file_df.to_csv(file_path, index=False)
        return None
    warnings.warn("This file is not a csv. Column renaming is ignored.", UserWarning)


def read_json(json_path):
    with open(json_path) as json_analyses:
        analyses_list = json.load(json_analyses)
    return analyses_list
