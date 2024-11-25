import zipfile
import json
import gzip

# Path to your JSON file
json_file = 'paprika_json.json'
# Path to the output .paprikarecipes file
paprika_file = 'mff_recipes.paprikarecipes'

# Read the JSON data from the file
with open(json_file, 'r') as file:
    recipes = json.load(file)

# Ensure recipes is a list
if not isinstance(recipes, list):
    recipes = [recipes]

# Create a .paprikarecipes ZIP archive
with zipfile.ZipFile(paprika_file, 'w') as zip_ref:
    # Iterate over each recipe
    for recipe in recipes:
        # Convert the recipe to a JSON string and then to bytes
        recipe_data = json.dumps(recipe).encode('utf-8')
        # Compress the JSON data using gzip
        compressed_data = gzip.compress(recipe_data)
        # Generate a filename for the .paprikarecipe file
        # Use the recipe's name or UID, ensure it's safe for filenames
        recipe_name = recipe.get('name', 'recipe').replace('/', '_')
        filename = f"{recipe_name}.paprikarecipe"
        # Add the compressed data as a .paprikarecipe file
        zip_ref.writestr(filename, compressed_data)

print(f"Created {paprika_file} with {len(recipes)} recipes.")