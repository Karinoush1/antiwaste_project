##################################################################################
import re                           # general 
import os
import streamlit as st              # application
from PIL import Image
from pyzbar.pyzbar import decode    # barcode
import openfoodfacts                # api
import spoonacular as sp
import requests
import boto3                        # AWS S3
import botocore
from translate import Translator    # translator

AWS_KEY_ID = "AKIA2PGNFKTIEM62XLP2" # os.environ["AWS_ACCESS_KEY_ID"] 
AWS_KEY_SECRET = "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" #os.environ["AWS_SECRET_ACCESS_KEY"]
S3_BUCKET = "antiwaste-bucket" #os.environ["S3_BUCKET"]


##################################################################################
# streamlit page setup
st.set_page_config(
    page_title="AntiWaste",
    page_icon="🗑️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# cacher le menu principal de l'application streamlit
hide_default_format = """
       <style>
       #MainMenu {visibility: hidden; }
       footer {visibility: hidden;}
       </style>
       """
st.markdown(hide_default_format, unsafe_allow_html=True)
       
# Spoonacular api key -> heroku
api = sp.API(os.environ["SPOONACULAR_API_KEY"])

# translator
translator= Translator(to_lang="fr")

# main page
st.write("## Antiwaste application")
st.write("This code is open source and available [antiwaste](https://github.com/cdouadi/antiwaste) on GitHub.")

# nombre de colonnes
nb_col = 4
col1, col2, col3, col4 = st.columns(nb_col)
column = [col1, col2, col3, col4]

# initialisation des session_state
if "input" not in st.session_state:
    st.session_state["input"] = ""
if "temp" not in st.session_state:
    st.session_state["temp"] = ""

##################################################################################
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
    return detectedBarcodes

##################################
# save uploaded file to local temporary directory
def save_uploaded_file_to_temp(uploaded_file):
    try:
        with open(uploaded_file.name, "wb") as f:
            f.write(uploaded_file.getvalue())
        return uploaded_file.name
    except Exception as e:
        st.exception("Failed to save file.")
        return None

##################################
# send to aws S3
def send_to_s3(bytes_data):
    session = boto3.Session(aws_access_key_id=AWS_KEY_ID,aws_secret_access_key=AWS_KEY_SECRET)
    s3 = session.resource("s3")
    bucket = s3.Bucket(S3_BUCKET)
    local_file_path = save_uploaded_file_to_temp(bytes_data)
    bucket.upload_file(local_file_path, "images/"+bytes_data.name)
    st.success("Image loaded successfully!")

##################################
def clear_text():
    st.session_state["temp"] = st.session_state["input"]
    st.session_state["input"] = ""


##################################################################################
def main():
    # 1. sidebar upload image (fruits, vegetables, product with barcode)
    with st.sidebar:
        st.write("## Upload :gear:")
        my_upload = st.file_uploader("🍍 Upload an image (fruits or product with barcode) 🥕", type=["png", "jpg", "jpeg"])
        bytes_data = my_upload
        if st.button("send to S3"):
            send_to_s3(bytes_data)
        col5, col6 = st.columns(2)

        input_text = st.text_input("🍇 Rajouter des ingredients 🍉: ", st.session_state["input"], key="input", 
                                placeholder="citron, concombre, pomme, carotte...", on_change=clear_text)
    
        input_text = st.session_state["temp"]


    product = []
    if my_upload is not None:
        detectedBarcodes = fix_image(upload=my_upload)
        for barcode in detectedBarcodes: 
            if barcode.data!="": 
                st.write(barcode.data)
                product.append(openfoodfacts.products.get_product(re.search(r'\d+', str(barcode.data)).group()))

        st.write("list barcode : ",product)

    # 2. search recipes by ingredients - spoonacular api
    with st.sidebar:
        ingredients="apple, flour, citron, sugar, banana, cornflakes"
        #st.write("👨‍🍳 vos ingrédients disponibles 🍽️: ",translator.translate(ingredients))
        st.selectbox("👨‍🍳 vos ingrédients disponibles 🍽️", [x for x in translator.translate(ingredients).split(",")] )

    response = api.search_recipes_by_ingredients(ingredients=ingredients, number=nb_col)
    data = response.json()

    
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
    
##################################################################################
if __name__ == '__main__':
    main()