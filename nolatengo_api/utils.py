import pandas as pd
import json, os

def convert_xlsx_to_json(filename):
    sheets = ['Hoja1']
    path = os.path.join('static', 'cards.json')

    # Read excel document
    for sheet in sheets:
        excel_data_df = pd.read_excel(filename, sheet_name=sheet)

        # Convert excel to jsonstring
        jsonObj = excel_data_df.to_json(orient='records')
        json_dict = json.loads(jsonObj)

        with open(path, 'w') as file:
            json.dump(json_dict, file, indent=4)
            print("The cards file was created in", path)
