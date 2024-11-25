import json
import uuid
import hashlib
from datetime import datetime
import requests
import base64
import zipfile
import json
import gzip

# Read the JSON data from 'recipes.json'
with open('mff_recipes.json', 'r') as file:
    data = json.load(file)

recipes_list = []

# Assuming the recipes are in data['rows']
for recipe_data in data.get('rows', []):
    # Extract fields
    name = recipe_data.get('parent_post', {}).get('post_title', None)
    ingredients_data = recipe_data.get('ingredients', [])
    instructions_data = recipe_data.get('instructions', [])
    categories_data = recipe_data.get('recipe', {})
    notes = recipe_data.get('recipe_notes', '')
    prep_time = recipe_data.get('prep_time', '')
    total_time = recipe_data.get('total_time', '')
    cook_time = recipe_data.get('cook_time', '')
    servings = recipe_data.get('servings', '')
    source_url = recipe_data.get('parent_post_url', '')
    created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    uid = str(uuid.uuid4()).upper()
    rating = recipe_data.get('rating', {}).get('average', None)
    description = recipe_data.get('tags', {}).get('course', [])
    if description:
        description = description[0].get('name', None)
    else:
        description = None
    photo_url = recipe_data.get('image_url', None)
    nutrition = recipe_data.get('nutrition', {})
    nutrition_info = f"{nutrition.get('calories', '')} calories per {nutrition.get('serving_size', '')} {nutrition.get('serving_unit', '')}\n\n{nutrition.get('carbohydrates', '')}g carbs | {nutrition.get('protein', '')}g protein | {nutrition.get('fat', '')}g fat"
    
    # Process ingredients
    ingredients_list = []
    for i, section in enumerate(ingredients_data):
        ingredients_list.append(section.get('name', ''))
        for ingredient in section.get('ingredients', []):
            amount = ingredient.get('amount', '')
            unit = ingredient.get('unit', '')
            name_ingredient = ingredient.get('name', '')
            notes_ingredient = ingredient.get('notes', '')
            ingredient_line = ' '.join(filter(None, [amount, unit, name_ingredient, notes_ingredient]))
            ingredients_list.append(ingredient_line.strip())
        
        if i < len(ingredients_data) - 1 and len(ingredients_list) > 1:
            ingredients_list.append('')

    ingredients = '\r\n'.join(ingredients_list)
                
    # Process instructions
    instructions_list = []
    for instruction in instructions_data:
        instruction_name = instruction.get('name', None)
        if instruction_name:
            print(f"Recipe: {name} \nInstruction name: {instruction_name}")
            instructions_list.append(instruction_name)

        instruction_steps = instruction.get('instructions', [])
        for step in instruction_steps:
            text = step.get('text', '')
            instructions_list.append(text.replace('<p>', '').replace('</p>', '').strip())


    directions = '\r\n\n'.join(instructions_list)
    
    # Download and encode photo
    photo_data = None
    photo_hash = None
    if photo_url:
        response = requests.get(photo_url)
        if response.status_code == 200:
            # Encode image data to Base64
            photo_data = base64.b64encode(response.content).decode('utf-8')
            # Compute photo hash
            photo_hash = hashlib.sha256(response.content).hexdigest().upper()
        else:
            print(f"Failed to download image from {photo_url}")
    
    # Create recipe dictionary matching example_json structure
    recipe = {
        'name': name,
        'ingredients': ingredients,
        'directions': directions,
        'categories': ["MacroFriendlyFood"],
        'notes': notes,
        'servings': servings,
        'source': "MacroFriendlyFood",  # Assuming empty as not provided
        'source_url': source_url,
        'prep_time': f"{prep_time} mins" if prep_time else '',
        'cook_time': f"{cook_time} mins" if cook_time else '',
        'total_time': f"{total_time} mins" if total_time else '',
        'rating': float(rating) if rating else None,
        'difficulty': '',
        'description': description if description else None,
        'created': created,
        'uid': uid,
        'photo': None,
        'photo_large': None,
        'photo_hash': photo_hash,
        'photo_data': photo_data,
        'photos': [],
        'hash': hashlib.sha256(name.encode('utf-8')).hexdigest().upper() if name else '',
        'nutritional_info': nutrition_info,
        'image_url': photo_url,
    }
    
    recipes_list.append(recipe)
    
# Write the output to 'converted_recipes.json'
with open('paprika_json.json', 'w') as outfile:
    json.dump(recipes_list, outfile, indent=2)

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