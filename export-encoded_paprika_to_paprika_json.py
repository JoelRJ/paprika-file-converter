import zipfile
import json
import gzip

# Path to your .paprikarecipes file
paprika_file = 'Pasta.paprikarecipes'

# List to hold all recipe data
recipes = []

# Open the .paprikarecipes file as a zip archive
with zipfile.ZipFile(paprika_file, 'r') as zip_ref:
    # Iterate over each file in the archive
    for file_info in zip_ref.infolist():
        if file_info.filename.endswith('.paprikarecipe'):
            # Read and decompress the JSON content from the .paprikarecipe file
            with zip_ref.open(file_info.filename) as recipe_file:
                with gzip.GzipFile(fileobj=recipe_file) as decompressed_file:
                    recipe_data = decompressed_file.read()
                    recipe_json = json.loads(recipe_data.decode('utf-8'))
                    recipes.append(recipe_json)

# Write the recipes list to 'paprika_file.json'
with open(paprika_file.split('.')[0] + '.json', 'w') as outfile:
    json.dump(recipes, outfile, indent=2)