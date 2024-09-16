import pytesseract
from PIL import Image, ImageEnhance, ImageOps
import requests
import cv2
import re
import os
import pytesseract
import platform

def MLmodel(image_link,entity_name):    
# Check the operating system and set the tesseract_cmd dynamically
    if platform.system() == 'Windows':
        tesseract_path = os.environ.get('TESSERACT_PATH', r"C:\Program Files\Tesseract-OCR\tesseract.exe")
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
    elif platform.system() == 'Linux':
        tesseract_path = os.environ.get('TESSERACT_PATH', '/usr/bin/tesseract')  # Default for Linux
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
    elif platform.system() == 'Darwin':  # macOS
        tesseract_path = os.environ.get('TESSERACT_PATH', '/usr/local/bin/tesseract')
        pytesseract.pytesseract.tesseract_cmd = tesseract_path

    # Check if tesseract exists
    if not os.path.exists(pytesseract.pytesseract.tesseract_cmd):
        raise FileNotFoundError("Tesseract executable not found! Please install Tesseract or set the TESSERACT_PATH environment variable.")

    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    # img_url = "https://m.media-amazon.com/images/I/812FE4kIZ8L.jpg"
    img_url = image_link
    img_path = requests.get(img_url, stream=True).raw
    img = Image.open(img_path)

    # converting the input image to grayscale kind of black and white so that text can be read properly without any shadow and all
    img_gray = ImageOps.grayscale(img)
    enhancer = ImageEnhance.Contrast(img_gray)
    img_enhanced = enhancer.enhance(2)  
    img_enhanced.save('temp_image.png')
    img_cv = cv2.imread('temp_image.png')
    img = 'temp_image.png'
    text = pytesseract.image_to_string(img)
    cleaned_text = text.strip().replace('\n', ' ').replace('/', ' ')
    words_array = cleaned_text.split()
    print(cleaned_text)
    # cleaned_text = " 440cm  45L"

    def extract_entities_from_text(text):
        pattern = r"(\d+(?:\.\d+)?)\s*([a-zA-Z ]+)"
        matches = re.findall(pattern, text)
        return matches

    matches = extract_entities_from_text(cleaned_text)
    print(f"matches:{matches}")

    entity_unit_map = {
        'width': {'centimetre', 'cm','foot','ft', 'inch', 'metre', 'm','millimetre','mm', 'yard'},
        'depth': {'centimetre','cm', 'foot','ft', 'inch', 'metre', 'm', 'millimetre','mm', 'yard'},
        'height': {'centimetre','cm', 'foot','ft', 'inch', 'metre', 'm', 'millimetre','mm', 'yard'},
        'item_weight': {'gram','gm','g','grams',
            'kilogram','kg', 
            'microgram',
            'milligram','mg',
            'ounce',
            'pound',
            'ton'},
        'maximum_weight_recommendation':{
            'gram','gm','g','grams',
            'kilogram','kg',
            'microgram',
            'milligram','mg',
            'ounce',
            'pound',
            'ton',
        },
        'voltage': {'kilovolt','kv', 'millivolt','mv', 'volt','v'},
        'wattage': {'kilowatt', 'watt'},
        'item_volume': {'centilitre','cl',
            'cubic foot',
            'cubic inch',
            'cup',
            'decilitre',
            'fluid ounce',
            'gallon',
            'imperial gallon',
            'litre','l',
            'microlitre',
            'millilitre','ml',
            'pint',
            'quart'}
    }

    allowed_units = {unit for entity in entity_unit_map for unit in entity_unit_map[entity]}

    # Define a dictionary for mapping different forms of the unit to a canonical form
    unit_mapping = {
        # Width, Depth, Height
        'centimetre': 'centimetre', 'cm': 'centimetre','centimetres': 'centimetre',
        'foot': 'foot', 'ft': 'foot',
        'inch': 'inch',
        'metre': 'metre', 'm':'meter',
        'millimetre': 'millimetre', 'mm': 'millimetre',
        'yard': 'yard',

        # Item Weight & Maximum Weight Recommendation
        'gram': 'gram', 'grams': 'gram', 'gm': 'gram', 'g': 'gram', 'G': 'gram',
        'kilogram': 'kg', 'kg': 'kg', 'Kilogram': 'kg',
        'microgram': 'microgram',
        'mg':  'milligram',
        'ounce': 'ounce',
        'pound': 'pound',
        'ton': 'ton',
        
        # Voltage
        'kilovolt': 'kilovolt', 'kv': 'kilovolt', 
        'millivolt': 'mv',  'mv': 'millivolt',
        'volt': 'volt', 'v': 'volt', 

        # Wattage
        'kilowatt': 'kilowatt', 'kw': 'kilowatt',
        'watt': 'watt', 'w': 'watt',

        # Item Volume
        'centilitre': 'cl', 'cl': 'cl',
        'cubic foot': 'cubic foot',
        'cubic inch': 'cubic inch',
        'cup': 'cup',
        'decilitre': 'decilitre',
        'fluid ounce': 'fluid ounce',
        'gallon': 'gallon',
        'imperial gallon': 'imperial gallon',
        'litre': 'litre', 'liter': 'litre', 'l': 'litre', 'L': 'litre',
        'microlitre': 'microlitre', 'microliter': 'microlitre',
        'millilitre': 'millilitre', 'ml': 'millilitre',
        'pint': 'pint',
        'quart': 'quart'
    }
    # Normalize the input and map to the canonical form
    def normalize_unit(unit):
        unit = unit.lower().strip()    
        if unit in unit_mapping:
            return unit_mapping[unit]    
        return unit

    def classify_entity(unit):
        for entity, units in entity_unit_map.items():
            if unit in units:
                return entity
        return None

    def finalMapper(): #ml model 
        result_dict = {}  # Dictionary to store intermediate results
        for match in matches:
            value, unit = match
            unit = unit.strip().lower()
            unit = normalize_unit(unit)

            if unit in allowed_units:
                entity = classify_entity(unit)
                if entity:
                    prediction = value + " " + unit
                    result_dict[entity] = prediction
                else:
                    result_dict[entity] = ""
        ans= ans = result_dict.get(entity_name, "")
        return ans
        # return "100 gram"

    result = finalMapper()
    return result
    # return "100 gram"
    # print(f"Result: {result}")
            
# image_link ="https://m.media-amazon.com/images/I/812FE4kIZ8L.jpg"
# res=MLmodel(image_link, entity_name="item_weight")   
# print(res)         

                



            
            
