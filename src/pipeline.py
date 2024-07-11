import pandas as pd
import json
from openai import OpenAI
import ast
API_KEY = ""
client = OpenAI(api_key = API_KEY)

def to_df(path):
    def json_to_dataframe(file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
            data = pd.json_normalize(data)
        
        # Ensure data is a list of dictionaries
        if isinstance(data, dict):
            data = [data]
        
        df = pd.DataFrame(data)
        return df
    df = json_to_dataframe(path)
    return df


def string_to_dict(string):
    try:
        # Use ast.literal_eval to safely evaluate the string as a dictionary
        dictionary = ast.literal_eval(string)
        return dictionary
    except (ValueError, SyntaxError):
        return "Invalid string format"


def create_row(df, dict, good_cols):
    df.rename(columns=dict, inplace=True)
    df = df[good_cols]
    return df


def get_column_dict(df):
    cols = list(df.columns)
    correct_cols = ["Timestamp", "Building", "Supplier", "RM_Num", "Sensor_Type", "Model_Num", "CO2", "Temperature", "Humidity", "Pressure"]
    message = f"Given this list of incorrect column names {cols} and the correct column names {correct_cols}, create a dictionary that maps the incorrect column names to the correct column names in this format: {{'incorrect1': 'correct1', 'incorrect2': 'correct2', ...}}. Do not include columns that do not fit within the correct column names list., the column data might be CO2"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant trying to create a renaming dictionary."},
            {"role": "user", "content": message}
        ]
    )
    res = response.choices[0].message.content
    dic = string_to_dict(res)
    return dic


def filter_first_instance(input_dict):
    unique_values = set()
    filtered_dict = {}

    for key, value in input_dict.items():
        if value not in unique_values:
            unique_values.add(value)
            filtered_dict[key] = value

    return filtered_dict


def create_db(list_of_rows):
    return pd.concat(list_of_rows, ignore_index=False)


def driver(path):
    df = to_df(path)
    dic = get_column_dict(df)
    dic = filter_first_instance(dic)
    correct_cols =dic.values()
    df = create_row(df, dic, correct_cols)
    return df
    

def main(paths):
    list_of_rows = []
    for path in paths:
        list_of_rows.append(driver(path))
    db = create_db(list_of_rows)
    return db




paths = ["../data/igor.json", "../data/enlink.json", "../data/airthings.json", "../data/kaiterra.json", "../data/quant.json", "../data/uhoo.json"]
db = main(paths)
