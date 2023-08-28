import os
import pandas as pd
import json
import requests

# Folder containing Excel files
FOLDER_PATH = 'C:\\Users\\User\\Desktop\\all_recipies2'
API_URL = 'https://su.lightfields.co/dishes/{dishId}/import-recipes'

def send_json_request(data, dish_id):
    headers = {'Content-Type': 'application/json'}
    response = requests.post(API_URL.replace('{dishId}', str(dish_id)), json=data, headers=headers)
    return response

for filename in os.listdir(FOLDER_PATH):
    reference_old_recipe = ""
    try:
        if filename.endswith(".xls") or filename.endswith(".xlsx"):
            file_path = os.path.join(FOLDER_PATH, filename)
            df = pd.read_excel(file_path, header=None)
    
            # Extract data from the top-left cells
            dish_id = df.iloc[0, 2]
            name = df.iloc[0, 1]
            reference_old_recipe = str(df.iloc[0, 0])
    
            # Set headers from the second row
            df.columns = df.iloc[1]
    
            # Drop the first two rows as they have been extracted and used
            df = df.drop([0, 1])
    
            # Create the JSON structure
            output = {
                "name": name,
                "portions": [1, 2, 3],
                "dietType": None,
                "carbohydrateSourceWeight": 0,
                "proteinSourceWeight": 0,
                "referenceOldRecipe": reference_old_recipe,
                "items": []
            }
    
            stack = [(output, 0)]  # Stack to track levels and corresponding dictionaries
    
            for _, row in df.iterrows():
                level = int(row['L'])
                item = {
                    "itemCode": row['Item Code'],
                    "quantity": row['Total Recp. Qty']
                }
    
                while stack[-1][1] >= level:
                    stack.pop()  # Pop levels that are higher or equal to the current level
    
                if level > 1:
                    parent_item = stack[-1][0]
                    if "items" not in parent_item:
                        parent_item["items"] = []
    
                    if level > stack[-1][1]:
                        item["compulsory"] = True
                    else:
                        item["compulsory"] = False
    
                    parent_item["items"].append(item)
                else:
                    output["items"].append(item)
    
                stack.append((item, level))
    
            # Convert the result into JSON
            json_result = json.dumps(output, indent=4)
            print("dishId =", dish_id)
            print(json_result)
            # Sending JSON request and handling response
            response = send_json_request(output, dish_id)
            if response.status_code == 201:
                print(f"{reference_old_recipe} created")
            else:
                print(f"Error creating {reference_old_recipe}: Status code {response.status_code}")
    except Exception:
        print(f"Error creating {reference_old_recipe}")
