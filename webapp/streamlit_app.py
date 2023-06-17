import streamlit as st
from PIL import Image
from pyzbar.pyzbar import decode
import openfoodfacts
import re
import spoonacular as sp
import os
from translate import Translator
import requests

# streamlit page setup
st.set_page_config(
    page_title="AntiWaste",
    page_icon="🗑️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Spoonacular api key -> heroku
api = sp.API(os.environ["SPOONACULAR_API_KEY"])

# translator
translator= Translator(to_lang="fr")

# main page
st.write("## Antiwaste application")
st.write("This code is open source and available [antiwaste](https://github.com/cdouadi/antiwaste) on GitHub.")
st.sidebar.write("## Upload :gear:")

# nombre de colonnes
nb_col = 4
col1, col2, col3, col4 = st.columns(nb_col)

# barcode detection 
def fix_image(upload):
    image = Image.open(upload)
    col1.write("Original Image :camera:")
    col1.image(image)

    detectedBarcodes = decode(image)
    
    # If not detected then print the message
    if not detectedBarcodes:
       st.write("Barcode Not Detected or your barcode is blank/corrupted!")
    else:
        for barcode in detectedBarcodes: 
            if barcode.data!="": 
            # Print the barcode data
                st.write(barcode.data)
                st.write(barcode.type)
        st.sidebar.markdown("\n")
    return detectedBarcodes


def main():
    # 1. sidebar upload image (fruits, vegetables, product with barcode)
    my_upload = st.sidebar.file_uploader("🍍 Upload an image (fruits or product with barcode) 🥕", type=["png", "jpg", "jpeg"])
    
    st.sidebar.button("prediction")
    product = []
    if my_upload is not None:
        detectedBarcodes = fix_image(upload=my_upload)
        for barcode in detectedBarcodes: 
            if barcode.data!="": 
                st.write(barcode.data)
                product.append(openfoodfacts.products.get_product(re.search(r'\d+', str(barcode.data)).group()))

        st.write("list barcode : ",product)

    # 2. search recipes by ingredients - spoonacular api
    ingredients="apple, flour, citron"
    st.write("La liste des ingrédients : ",translator.translate(ingredients))
    response = api.search_recipes_by_ingredients(ingredients=ingredients, number=nb_col)
    data = response.json()

    column = [col1, col2, col3, col4]
    # 3. parcours des recettes et affichage d'une recette par colonne (col1,...)
    for i,recipe in enumerate(data):
        url = recipe['image']
        # translation of title recipe
        translation = translator.translate(recipe['title'])
        column[i].write(translation)

        # check if the image is available (spoonacular api).
        response = requests.head(url)
        if response.status_code == 200:
            # des fois spoonacular n'a pas d'images.
            # column[i].write(recipe['image'])
            column[i].image(recipe['image'])
        else:
            column[i].write("💔 The image is not available 😢")

if __name__ == '__main__':
    main()