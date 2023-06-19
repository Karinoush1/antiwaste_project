##################################################################################
import re                           # general 
import os
import streamlit as st              # application
from PIL import Image
import numpy as np                  # machine learning
from tensorflow.keras.applications.mobilenet import preprocess_input
from keras.models import load_model
from tensorflow.keras.preprocessing import image

import numpy as np
from pyzbar.pyzbar import decode    # barcode
import openfoodfacts                # api
import spoonacular as sp
import requests
import boto3                        # AWS S3
import botocore
from translate import Translator    # translator

AWS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"] 
AWS_KEY_SECRET = os.environ["AWS_SECRET_ACCESS_KEY"]
S3_BUCKET = os.environ["S3_BUCKET"]
fruits_and_vegetables = [ "Apple Braeburn", "Apple Crimson Snow", "Apple Golden 1", "Apple Golden 2", "Apple Golden 3", "Apple Granny Smith", "Apple Pink Lady", "Apple Red 1", "Apple Red 2", "Apple Red 3", "Apple Red Delicious", "Apple Red Yellow 1", "Apple Red Yellow 2", "Apricot", "Avocado", "Avocado ripe", "Banana", "Banana Lady Finger", "Banana Red", "Beetroot", "Blueberry", "Cactus fruit", "Cantaloupe 1", "Cantaloupe 2", "Carambula", "Cauliflower", "Cherry 1", "Cherry 2", "Cherry Rainier", "Cherry Wax Black", "Cherry Wax Red", "Cherry Wax Yellow", "Chestnut", "Clementine", "Cocos", "Corn", "Corn Husk", "Cucumber Ripe", "Cucumber Ripe 2", "Dates", "Eggplant", "Fig", "Ginger Root", "Granadilla", "Grape Blue", "Grape Pink", "Grape White", "Grape White 2", "Grape White 3", "Grape White 4", "Grapefruit Pink", "Grapefruit White", "Guava", "Hazelnut", "Huckleberry", "Kaki", "Kiwi", "Kohlrabi", "Kumquats", "Lemon", "Lemon Meyer", "Limes", "Lychee", "Mandarine", "Mango", "Mango Red", "Mangostan", "Maracuja", "Melon Piel de Sapo", "Mulberry", "Nectarine", "Nectarine Flat", "Nut Forest", "Nut Pecan", "Onion Red", "Onion Red Peeled", "Onion White", "Orange", "Papaya", "Passion Fruit", "Peach", "Peach 2", "Peach Flat", "Pear", "Pear 2", "Pear Abate", "Pear Forelle", "Pear Kaiser", "Pear Monster", "Pear Red", "Pear Stone", "Pear Williams", "Pepino", "Pepper Green", "Pepper Orange", "Pepper Red", "Pepper Yellow", "Physalis", "Physalis with Husk", "Pineapple", "Pineapple Mini", "Pitahaya Red", "Plum", "Plum 2", "Plum 3", "Pomegranate", "Pomelo Sweetie", "Potato Red", "Potato Red Washed", "Potato Sweet", "Potato White", "Quince", "Rambutan", "Raspberry", "Redcurrant", "Salak", "Strawberry", "Strawberry Wedge","Tamarillo","Tangelo","Tomato 1","Tomato 2","Tomato 3","Tomato 4","Tomato Cherry Red","Tomato Heart","Tomato Maroon","Tomato Yellow","Tomato not Ripened","Walnut","Watermelon"]

##################################################################################
# streamlit page setup
st.set_page_config(
    page_title="AntiWaste",
    page_icon="🗑️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# cacher le menu principal de l'application streamlit
#hide_default_format = """
#       <style>
#       #MainMenu {visibility: hidden; }
#       footer {visibility: hidden;}
#       </style>
#       """
#st.markdown(hide_default_format, unsafe_allow_html=True)
       
# Spoonacular api key -> heroku
api = sp.API(os.environ["SPOONACULAR_API_KEY"])

# translator
translator= Translator(to_lang="fr")

# main page
st.write("## Antiwaste application")
st.write("This code is open source and available [antiwaste](https://github.com/cdouadi/antiwaste) on GitHub.")



# initialisation des session_state
if "input" not in st.session_state:
    st.session_state["input"] = ""
if "temp" not in st.session_state:
    st.session_state["temp"] = ""

##################################################################################
# barcode detection 
def fix_image(upload):
    imagefile = Image.open(upload)
    col1.write("Original Image :camera:")
    col1.image(imagefile)

    detectedBarcodes = decode(imagefile)
    
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
def send_to_s3(my_upload):
    session = boto3.Session(aws_access_key_id=AWS_KEY_ID,aws_secret_access_key=AWS_KEY_SECRET)
    s3 = session.resource("s3")
    bucket = s3.Bucket(S3_BUCKET)
    local_file_path = save_uploaded_file_to_temp(my_upload)
    bucket.upload_file(local_file_path, "images/"+my_upload.name)
    st.success("Image loaded successfully!")

##################################
def clear_text():
    st.session_state["temp"] = st.session_state["input"]
    st.session_state["input"] = ""

##################################
def prepare_image(file):
    img = image.load_img(file, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array_expanded_dims = np.expand_dims(img_array, axis=0)
    return preprocess_input(img_array_expanded_dims)

##################################################################################
def main():
    # 1. sidebar upload image (fruits, vegetables, product with barcode)
    with st.sidebar:
        st.write("## Upload :gear:")
        my_upload = st.file_uploader("🍍 Upload an image (fruits or product with barcode) 🥕", type=["png", "jpg", "jpeg"])
        if st.button("send to S3"):
            send_to_s3(my_upload)
        col5, col6 = st.columns(2)

        input_text = st.text_input("🍇 Rajouter des ingredients 🍉: ", st.session_state["input"], key="input", 
                                placeholder="citron, concombre, pomme, carotte...", on_change=clear_text)
        #input_text = st.session_state["temp"]

    product = []
    if my_upload is not None:
        detectedBarcodes = fix_image(upload=my_upload)
        for barcode in detectedBarcodes: 
            if barcode.data!="": 
                st.write(barcode.data)
                product.append(openfoodfacts.products.get_product(re.search(r'\d+', str(barcode.data)).group()))

        st.write("list barcode : ",product)

    # 1. prediction modele
    model = load_model('model/TransferLearningModel_10epochs_lr0.0001_validation.h5')
    uploaded_file = st.file_uploader("Upload an image for prediction", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        imagefile2 = Image.open(uploaded_file)
        newsize = (400, 500)
        imagefile2 = imagefile2.resize(newsize)
        st.image(imagefile2)

        if st.button("predict"):
            predictions = model.predict(prepare_image(uploaded_file))
            pred = np.argmax(predictions)
            #st.write(fruits_and_vegetables[pred])
            st.success("prediction is available !")
    
    # 2. search recipes by ingredients - spoonacular api
            with st.sidebar:
                ingredients="apple, flour, citron, sugar"
                ingredients = ingredients + ", " + fruits_and_vegetables[pred].split()[0]
                #st.write("👨‍🍳 vos ingrédients disponibles 🍽️: ",translator.translate(ingredients))
                st.selectbox("👨‍🍳 vos ingrédients disponibles 🍽️", [x for x in translator.translate(ingredients).split(",")] )

            response = api.search_recipes_by_ingredients(ingredients=ingredients, number=4)
            data = response.json()
            
            # 3. parcours des recettes et affichage d'une recette par colonne (col1,...)
            # nombre de colonnes
            nb_col = 4
            col1, col2, col3, col4 = st.columns(nb_col)
            column = [col1, col2, col3, col4]
            
            for i,recipe in enumerate(data):
                ######## rajouter exception quota reached 150 per day
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