import streamlit as st
from PIL import Image
from io import BytesIO
import base64
import time
import cv2
from pyzbar.pyzbar import decode
import openfoodfacts
import re


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

col1, col2 = st.columns(2)
my_upload = st.sidebar.file_uploader("🍍 Upload an image 🥕", type=["png", "jpg", "jpeg"])
st.write(my_upload)

product = []
if my_upload is not None:
    detectedBarcodes = fix_image(upload=my_upload)
    for barcode in detectedBarcodes: 
        if barcode.data!="": 
            st.write(barcode.data)
            product.append(openfoodfacts.products.get_product(re.search(r'\d+', str(barcode.data)).group()))

    st.write("list barcode : ",product)

#st.sidebar.download_button("Submit image", "fixed.png", "image/png")

with st.spinner(text='In progress'):
   time.sleep(5)
   st.sidebar.success('Done')

st.sidebar.error('Error message')
st.sidebar.warning('Warning message')
st.sidebar.info('Info message')
st.sidebar.success('Success message')

#st.balloons()
#st.snow()
#st.exception(e)

progress_text = "Operation in progress. Please wait."
my_bar = st.sidebar.progress(0, text=progress_text)

for percent_complete in range(100):
    time.sleep(0.1)
    my_bar.progress(percent_complete + 1, text=progress_text)