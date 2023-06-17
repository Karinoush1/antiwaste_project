import streamlit as st
from PIL import Image
from io import BytesIO
import base64
import time
from pyzbar.pyzbar import decode
import openfoodfacts
import re
import spoonacular as sp
import os
from translate import Translator
import requests


st.set_page_config(
    page_title="AntiWaste",
    page_icon="🗑️",
    layout="wide"
)

st.write("## Antiwaste application")
st.write("This code is open source and available [antiwaste](https://github.com/cdouadi/antiwaste) on GitHub.")
st.sidebar.write("## Upload :gear:")

#picture = st.sidebar.camera_input("🥑 Take photo 📸")
#if picture:
#    st.image(picture)


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
# nombre de colonnes
nb_col = 4
col1, col2, col3, col4 = st.columns(nb_col)
my_upload = st.sidebar.file_uploader("🍍 Upload an image 🥕", type=["png", "jpg", "jpeg"])

st.sidebar.button("prediction")
product = []
if my_upload is not None:
    detectedBarcodes = fix_image(upload=my_upload)
    for barcode in detectedBarcodes: 
        if barcode.data!="": 
            st.write(barcode.data)
            product.append(openfoodfacts.products.get_product(re.search(r'\d+', str(barcode.data)).group()))

    st.write("list barcode : ",product)

#api = sp.API(os.environ["SPOONACULAR_API_KEY"])
api = sp.API("c135fe564b084d9bb1eedd248a56d637")

# search recipes by ingredients
response = api.search_recipes_by_ingredients(ingredients="apple, flour, citron", number=nb_col)

data = response.json()

# translator
translator= Translator(to_lang="fr")


column = [col1, col2, col3, col4]

for recipe, i in zip(data, range(0,nb_col,1)):
    url = recipe['image']
    # translation
    translation = translator.translate(recipe['title'])
    column[i].write(translation)


    response = requests.head(url)
    if response.status_code == 200:
        # des fois spoonacular n'a pas d'images.
        #column[i].write(recipe['image'])
        column[i].image(recipe['image'])
    else:
        column[i].write("💔 The image is not available 😢")

    i += 1



#import datetime
#st.sidebar.subheader("Prédition de la demande")
#timeOfTheDay= st.sidebar.time_input("Choisir l'heure", datetime.time(8, 45,00))
#st.sidebar.write('Heure:', timeOfTheDay)
#st.sidebar.markdown("Renseignez vos coordonnées GPS")
## latitude
#latitude= st.sidebar.number_input("Choisir la latitude ", min_value=0,max_value=50)
#longitude= st.sidebar.number_input("Choisir la longitude ", min_value=0,max_value=50)
#st.sidebar.write('Vos coordonnées GPS (latitude,longitude) : ', (latitude,longitude))




