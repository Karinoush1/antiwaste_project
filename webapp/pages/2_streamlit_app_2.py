#from mylib.imports import clickable_images, switch_page, st, base64
#from mylib.fonctions import add_bg_from_local
import os
import re  # general
import sys
import datetime

sys.path.append("pages")

import boto3  # AWS S3
import botocore

import numpy as np  # machine learning
import pandas as pd

import openfoodfacts  # api
import requests
import spoonacular as sp

from PIL import Image
from pyzbar.pyzbar import decode  # barcode

import streamlit as st  # application
import streamlit.components.v1 as components
from streamlit_option_menu import option_menu
from streamlit_extras.buy_me_a_coffee import button
from streamlit_extras.customize_running import center_running
from streamlit_extras.badges import badge
from streamlit_app import *

from translate import Translator  # translator

from keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.mobilenet import preprocess_input

AWS_KEY_ID = "AKIA2PGNFKTIEM62XLP2" # os.environ["AWS_ACCESS_KEY_ID"] 
AWS_KEY_SECRET = "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" #os.environ["AWS_SECRET_ACCESS_KEY"]
S3_BUCKET = "antiwaste-bucket" #os.environ["S3_BUCKET"]
fruits_and_vegetables = [ "Apple Braeburn", "Apple Crimson Snow", "Apple Golden 1", "Apple Golden 2", "Apple Golden 3", "Apple Granny Smith", "Apple Pink Lady", "Apple Red 1", "Apple Red 2", "Apple Red 3", "Apple Red Delicious", "Apple Red Yellow 1", "Apple Red Yellow 2", "Apricot", "Avocado", "Avocado ripe", "Banana", "Banana Lady Finger", "Banana Red", "Beetroot", "Blueberry", "Cactus fruit", "Cantaloupe 1", "Cantaloupe 2", "Carambula", "Cauliflower", "Cherry 1", "Cherry 2", "Cherry Rainier", "Cherry Wax Black", "Cherry Wax Red", "Cherry Wax Yellow", "Chestnut", "Clementine", "Cocos", "Corn", "Corn Husk", "Cucumber Ripe", "Cucumber Ripe 2", "Dates", "Eggplant", "Fig", "Ginger Root", "Granadilla", "Grape Blue", "Grape Pink", "Grape White", "Grape White 2", "Grape White 3", "Grape White 4", "Grapefruit Pink", "Grapefruit White", "Guava", "Hazelnut", "Huckleberry", "Kaki", "Kiwi", "Kohlrabi", "Kumquats", "Lemon", "Lemon Meyer", "Limes", "Lychee", "Mandarine", "Mango", "Mango Red", "Mangostan", "Maracuja", "Melon Piel de Sapo", "Mulberry", "Nectarine", "Nectarine Flat", "Nut Forest", "Nut Pecan", "Onion Red", "Onion Red Peeled", "Onion White", "Orange", "Papaya", "Passion Fruit", "Peach", "Peach 2", "Peach Flat", "Pear", "Pear 2", "Pear Abate", "Pear Forelle", "Pear Kaiser", "Pear Monster", "Pear Red", "Pear Stone", "Pear Williams", "Pepino", "Pepper Green", "Pepper Orange", "Pepper Red", "Pepper Yellow", "Physalis", "Physalis with Husk", "Pineapple", "Pineapple Mini", "Pitahaya Red", "Plum", "Plum 2", "Plum 3", "Pomegranate", "Pomelo Sweetie", "Potato Red", "Potato Red Washed", "Potato Sweet", "Potato White", "Quince", "Rambutan", "Raspberry", "Redcurrant", "Salak", "Strawberry", "Strawberry Wedge","Tamarillo","Tangelo","Tomato 1","Tomato 2","Tomato 3","Tomato 4","Tomato Cherry Red","Tomato Heart","Tomato Maroon","Tomato Yellow","Tomato not Ripened","Walnut","Watermelon"]
api = sp.API(os.environ["SPOONACULAR_API_KEY"]) # Spoonacular api key -> heroku
translator = Translator(to_lang="fr", from_lang="en")    # translator
translator_reverse= Translator(to_lang="en", from_lang="fr")


saisons=[
{ "fruits": ["ananas", "avocat", "banane", "citron", "clementine", "datte", "fruit de la passion", "grenade", "kaki", "kiwi", "litchi", "mandarine", "mangue", "orange", "orange sanguine", "pamplemousse", "papaye", "poire", "pomme"], "legumes": ["carotte", "celeri", "celeri branche", "celeri rave", "chou blanc", "chou de bruxelles", "chou frise", "chou rouge", "chou-chinois", "cima di rapa", "citrouille", "cresson", "endive", "mache", "oignon", "poireau", "pomme de terre", "salsifis", "topinambour"]},
{ "fruits": ["ananas", "avocat", "banane", "citron", "clementine", "datte", "fruit de la passion", "grenade", "kiwi", "litchi", "mandarine", "mangue", "orange", "orange sanguine", "pamplemousse", "papaye", "pomme"], "legumes": ["carotte", "celeri", "celeri branche", "celeri rave", "chou blanc", "chou frise", "chou rouge", "chou-chinois", "cima di rapa", "citrouille", "endive", "mache", "oignon", "poireau", "pomme de terre", "salsifis", "topinambour"]},
{ "fruits": ["ananas", "avocat", "banane", "citron", "datte", "fruit de la passion", "kiwi", "mandarine", "mangue", "orange sanguine", "pamplemousse", "papaye", "pomme"], "legumes": ["carotte", "celeri", "chou blanc", "chou frise", "chou rouge", "chou-rave", "cima di rapa", "endive", "oignon", "petit oignon blanc", "poireau", "salsifis"]},
{ "legumes": ["ail", "asperge blanche", "bette", "carotte", "chou blanc", "chou rouge", "chou-rave", "epinard", "laitue romaine", "oignon", "petit oignon blanc", "radis"], "fruits": ["avocat", "banane", "citron", "fruit de la passion", "kiwi", "litchi", "mangue", "papaye"]},
{ "legumes": ["ail", "asperge blanche", "asperge verte", "aubergine", "bette", "betterave rouge", "chou frise", "chou-chinois", "chou-fleur", "chou-rave", "concombre", "epinard", "fenouil", "laitue romaine", "petit oignon blanc", "pomme de terre", "radis", "radis long", "rhubarbe"], "fruits": ["avocat", "banane", "citron", "fraise", "fraise des bois", "fruit de la passion", "kiwi", "mangue", "papaye"]},
{ "legumes": ["ail", "artichaut", "asperge blanche", "asperge verte", "aubergine", "bette", "betterave rouge", "brocoli", "chou blanc", "chou frise", "chou romanesco", "chou rouge", "chou-chinois", "chou-fleur", "chou-rave", "concombre", "courgette", "epinard", "fenouil", "haricot", "laitue romaine", "navet", "petit oignon blanc", "petit pois", "pois mange-tout", "poivron", "pomme de terre", "radis", "radis long", "rhubarbe"], "fruits": ["banane", "cerise", "citron", "fraise", "fraise des bois", "framboise", "fruit de la passion", "groseille", "groseille i maquereau", "litchi", "mangue", "melon", "nectarine", "papaye", "pasteque", "peche", "tomate", "tomate charnue", "tomate peretti"]},
{ "fruits": ["abricot", "airelle", "banane", "cassis", "cerise", "citron", "fraise", "fraise des bois", "framboise", "fruit de la passion", "groseille", "groseille i maquereau", "litchi", "mangue", "melon", "mure", "myrtille", "nectarine", "papaye", "pasteque", "peche", "tomate", "tomate charnue", "tomate peretti"], "legumes": ["ail", "artichaut", "aubergine", "bette", "betterave rouge", "brocoli", "chou blanc", "chou frise", "chou romanesco", "chou rouge", "chou-chinois", "chou-fleur", "chou-rave", "concombre", "courgette", "cresson", "epinard", "fenouil", "haricot", "laitue romaine", "ma\u00efs", "navet", "patisson", "petit oignon blanc", "petit pois", "pois mange-tout", "poivron", "pomme de terre", "potiron", "radis", "radis long"]},
{ "fruits": ["abricot", "airelle", "amande", "banane", "cassis", "cerise", "citron", "datte", "figue fraiche", "fraise", "fraise des bois", "framboise", "fruit de la passion", "groseille i maquereau", "litchi", "mangue", "marron", "melon", "mirabelle", "mure", "myrtille", "nectarine", "noisette", "papaye", "pasteque", "peche", "poire", "prune", "quetsche", "reine-claude", "tomate", "tomate charnue", "tomate peretti"], "legumes": ["ail", "artichaut", "aubergine", "bette", "betterave rouge", "brocoli", "carotte", "catalonia", "chou blanc", "chou de bruxelles", "chou frise", "chou romanesco", "chou rouge", "chou-chinois", "chou-fleur", "chou-rave", "concombre", "courge", "courgette", "cresson", "epinard", "fenouil", "haricot", "laitue romaine", "ma\u00efs", "navet", "oignon", "patisson", "petit oignon blanc", "poivron", "pomme de terre", "potiron", "radis long"]},
{ "fruits": ["amande", "avocat", "banane", "chataigne", "citron", "coing", "datte", "figue fraiche", "framboise", "fruit de la passion", "litchi", "mangue", "marron", "melon", "mirabelle", "mure", "myrtille", "nectarine", "noisette", "noix", "papaye", "pasteque", "peche", "poire", "prune", "quetsche", "raisin", "reine-claude", "tomate", "tomate charnue", "tomate peretti"], "legumes": ["artichaut", "aubergine", "bette", "betterave rouge", "brocoli", "carotte", "catalonia", "celeri branche", "celeri rave", "chou blanc", "chou de bruxelles", "chou frise", "chou romanesco", "chou rouge", "chou-chinois", "chou-fleur", "chou-rave", "citrouille", "concombre", "courge", "courgette", "cresson", "epinard", "fenouil", "haricot", "laitue romaine", "ma\u00efs", "navet", "oignon", "panais", "patisson", "petit oignon blanc", "poireau", "poivron", "pomme de terre", "potiron"]},
{ "fruits": ["avocat", "banane", "chataigne", "citron", "coing", "datte", "figue fraiche", "fruit de la passion", "kaki", "litchi", "mandarine", "mangue", "marron", "noisette", "noix", "papaye", "poire", "pomme", "prune", "quetsche", "raisin"], "legumes": ["bette", "betterave rouge", "brocoli", "carotte", "catalonia", "celeri", "celeri branche", "celeri rave", "chou blanc", "chou de bruxelles", "chou frise", "chou rouge", "chou-chinois", "chou-fleur", "chou-rave", "cima di rapa", "citrouille", "courge", "cresson", "epinard", "fenouil", "laitue romaine", "ma\u00efs", "oignon", "panais", "petit oignon blanc", "poireau", "poivron", "pomme de terre", "potimarron", "potiron", "salsifis", "topinambour"]},
{ "fruits": ["ananas", "avocat", "banane", "chataigne", "citron", "clementine", "datte", "fruit de la passion", "grenade", "kaki", "kiwi", "kumquat", "mandarine", "mangue", "marron", "noix", "orange", "papaye", "poire", "pomme"], "legumes": ["carotte", "catalonia", "celeri", "celeri branche", "celeri rave", "chou blanc", "chou de bruxelles", "chou frise", "chou rouge", "chou-chinois", "chou-rave", "cima di rapa", "citrouille", "courge", "cresson", "endive", "epinard", "fenouil", "mache", "oignon", "panais", "poireau", "pomme de terre", "potimarron", "salsifis", "topinambour"]},
{ "fruits": ["ananas", "avocat", "banane", "chataigne", "citron", "clementine", "datte", "fruit de la passion", "grenade", "kaki", "kiwi", "kumquat", "litchi", "mandarine", "mangue", "marron", "orange", "orange sanguine", "pamplemousse", "papaye", "poire", "pomme"], "legumes": ["carotte", "catalonia", "celeri", "celeri branche", "celeri rave", "chou blanc", "chou de bruxelles", "chou frise", "chou rouge", "chou-chinois", "cima di rapa", "citrouille", "courge", "cresson", "endive", "mache", "oignon", "panais", "poireau", "pomme de terre", "salsifis", "topinambour"]}
]




def fix_image(upload):
    imagefile = Image.open(upload)
    newsize = (400, 500)
    imagefile = imagefile.resize(newsize)
    col7, col8 = st.columns(2)
    col7.write("Original Image :camera:")
    col7.image(imagefile)
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


# save uploaded file to local temporary directory
def save_uploaded_file_to_temp(uploaded_file):
    try:
        with open(uploaded_file.name, "wb") as f:
            f.write(uploaded_file.getvalue())
        return uploaded_file.name
    except Exception as e:
        st.exception("Failed to save file.")
        return None

# send to aws S3
def send_to_s3(my_upload):
    session = boto3.Session(aws_access_key_id=AWS_KEY_ID,aws_secret_access_key=AWS_KEY_SECRET)
    s3 = session.resource("s3")
    bucket = s3.Bucket(S3_BUCKET)
    local_file_path = save_uploaded_file_to_temp(my_upload)
    bucket.upload_file(local_file_path, "images/"+my_upload.name)
    st.success("Image loaded successfully!")

def clear_text():
    st.session_state["temp"] = st.session_state["input"]
    st.session_state["input"] = ""


def prepare_image(file):
    img = image.load_img(file, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array_expanded_dims = np.expand_dims(img_array, axis=0)
    return preprocess_input(img_array_expanded_dims)

def api_call(pred):
    # 2. search recipes by ingredients - spoonacular api
    ingredients = ", ".join(str(x) for x in st.session_state.liste_finale)
    st.write("ingrédients : ",ingredients)
    for element in st.session_state.liste_finale:
        de_saison(element)

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

def fruits():
    # 1. prediction modele
    st.subheader("Step 1: take a picture or upload an image of your fruits and vegetables")
    mode_dev = st.checkbox('mode developpeur')
    if mode_dev:
        modele =["TransferLearningModel_10epochs_lr0.0001_validation.h5", "Inception V3", "YoloV8"]
        choix_model = st.selectbox("modele deep learning", modele)
        model = load_model(f'model/{choix_model}')
    else :
        model=load_model('model/TransferLearningModel_10epochs_lr0.0001_validation.h5')
    uploaded_file = st.file_uploader("🍍 Upload an image to predict", type=["png", "jpg", "jpeg"])
    
    if uploaded_file is not None:
        imagefile2 = Image.open(uploaded_file)
        newsize = (400, 500)
        imagefile2 = imagefile2.resize(newsize)
        st.image(imagefile2)

        if st.button("predict"):
            center_running()
            predictions = model.predict(prepare_image(uploaded_file))
            pred = np.argmax(predictions)
            ingredient = translator.translate(fruits_and_vegetables[pred].split()[0])
            st.session_state.liste_ingredients[ingredient] = ingredient
            st.session_state.data.append(ingredient)
            st.success(f"prediction is available : {ingredient}")

def barcode():
    # 1. sidebar upload image (fruits, vegetables, product with barcode)
    st.subheader("Step 2: take a picture or upload an image of your barcode")
    my_upload = st.file_uploader("🍍 Upload an image (fruits or product with barcode) 🥕", type=["png", "jpg", "jpeg"])

    if st.button("send to S3"):
        send_to_s3(my_upload)
        col5, col6 = st.columns(2)
        st.divider()
        input_text = st.text_input("🍇 Rajouter des ingredients 🍉: ", st.session_state["input"], key="input", 
                                placeholder="citron, concombre, pomme, carotte...", on_change=clear_text)
        #input_text = st.session_state["temp"]
        
    product = []
    if my_upload is not None:
        detectedBarcodes = fix_image(upload=my_upload)
        for barcode in detectedBarcodes: 
            if barcode.data!="": 
                response = openfoodfacts.products.get_product(re.search(r'\d+', str(barcode.data)).group())
                product.append(openfoodfacts.products.get_product(re.search(r'\d+', str(barcode.data)).group()))
        ingredient = response["product"]["product_name"]
        st.session_state.liste_ingredients[ingredient] = ingredient
        st.session_state.data.append(ingredient)

def about():
    st.subheader("Code-source")
    col1, col2, col3 = st.columns([1,1,6])
    with col1:
        badge(type="github", name="cdouadi/antiwaste")
    counter ="""visiteurs site: <a><img src="https://www.cutercounter.com/hits.php?id=hvuxnofxa&nd=6&style=1" border="0" alt="counter"></a>"""
    
    col2.markdown(counter, unsafe_allow_html=True)
    
    st.info("👨‍💻 The application is open source and available on GitHub.")
    st.subheader("TEAM 🚀")
    st.info(" Juliette, Iheb, Karina, Frederic et Chakib")

    st.info("🪐 Special thanks to Jedha Team 👨‍🏫 : Charles - Aurélie - Antoine D. - Océane - Antoine C. - Mathieu - Lionel et Antoine K.")
  

    # buy me a coffee link
    col3, col4 = st.columns([6,1])
    with col4:
        button(username="dchakib", floating=False, width=221)


def another():
    with st.container():
        # Store uploaded photos in session_state
        if 'photos' not in st.session_state:
            st.session_state.photos = []

        # File uploader for photos
        uploaded_files = st.file_uploader("Upload an image (fruits or product with barcode) 🥕", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

        # Process uploaded files
        if uploaded_files:
            for file in uploaded_files:
                st.session_state.photos.append(file)

        # Display the uploaded photos
        if st.session_state.photos:
            st.write('Uploaded Photos:')
            for photo in st.session_state.photos:
                st.image(photo)

def de_saison(ingredient):
    mois = datetime.date.today().month
    liste_saison = saisons[mois]
    if ingredient in liste_saison['fruits'] or ingredient in liste_saison['legumes']:
        return True
    else:
        return False


# streamlit page setup
st.set_page_config(
    page_title="Welcome to SAVE",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)



# initialisation des session_state
if 'data' not in st.session_state:
    st.session_state['data'] = []
if 'liste_ingredients' not in st.session_state:
    st.session_state['liste_ingredients'] = {}
if 'liste_finale' not in st.session_state:
    st.session_state['liste_finale'] = pd.DataFrame()


liste_menu = ["Prediction", "Barcode", 'Recettes', 'Conseils', 'A propos']
selected = liste_menu[0]
selected = option_menu(None, liste_menu,icons=["list-task","list-task","list-task", "list-task", "list-task"], menu_icon="cast", default_index=0, orientation="horizontal")


def main():
    pred = -1
    
    # sidebar tips anti gaspillage
    st.sidebar.image("tips.jpg")
    
    # fruits & vegetables process
    if selected == liste_menu[0]:
        fruits()
    
    # barcode process
    if selected == liste_menu[1]:
        barcode()

    # display recipes
    if selected == liste_menu[2]:
        data = pd.read_csv('./Biodata.csv')
        if len(st.session_state.liste_ingredients) != 0 or len(st.session_state.data) !=0:
            data = pd.concat([data['compo'], pd.DataFrame.from_dict(st.session_state.data)],ignore_index=True)
            options = st.multiselect("rajouter des ingredients",data, default= pd.Series(st.session_state.liste_ingredients.keys()) )
            if st.button("valider"):
                st.session_state.liste_finale = [translator_reverse.translate(x) for x in options]
                api_call(pred)
    
    if selected == liste_menu[3]:
        st.divider()
        
        st.subheader("Calendrier des fruits et légumes de saison")
        col1, col2 = st.columns(2)
        col1.image('1.jpg')
        col2.image('2.jpg')
        
        st.divider()
        col3, col4 = st.columns(2)
        with col3:
            st.subheader("Un peu de data... Emission CO2")
            st.image("tableau_d_emission.jpg", caption='Ces catégories ne sont pas des chiffres officiels. Ils ne peuvent en aucun cas être utilisés comme référence.')

        with col4:
            st.subheader("Vidéo :video_camera:")
            st.text("Si tu souhaites en savoir plus sur le gaspillage alimentaire tu peux regarder les vidéos ci-dessous :")
            with st.expander("⏯️ Prévention anti-gaspillage", expanded=True):
                st.video("https://www.youtube.com/watch?v=rjxwfp8rs34")
            with st.expander("⏯️ Gaspillage et réchauffement climatique"):
                st.video("https://www.youtube.com/watch?v=ishA6kry8nc")
            with st.expander("⏯️ Empreinte carbonne du gaspillage alimentaire"):
                st.video("https://www.youtube.com/watch?v=IoCVrkcaH6Q")

    # page about
    if selected == liste_menu[4]:
        about()


if __name__ == '__main__':    
    main()