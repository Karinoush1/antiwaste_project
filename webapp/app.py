import streamlit as st
from PIL import Image
from io import BytesIO
import base64
import time

st.set_page_config(
    page_title="AntiWaste",
    page_icon="🗑️",
    layout="wide"
)

st.write("## Antiwaste application")
st.write("This code is open source and available [antiwaste](https://github.com/cdouadi/antiwaste) on GitHub.")
st.sidebar.write("## Upload :gear:")
picture = st.sidebar.camera_input("🥑 Take photo 📸")


if picture:
    st.image(picture)


def fix_image(upload):
    image = Image.open(upload)
    col1.write("Original Image :camera:")
    col1.image(image)

    st.sidebar.markdown("\n")


col1, col2 = st.columns(2)
my_upload = st.sidebar.file_uploader("🍍 Upload an image 🥕", type=["png", "jpg", "jpeg"])

if my_upload is not None:
    fix_image(upload=my_upload)

st.sidebar.write("\n\n\n")
st.sidebar.download_button("Submit image", "fixed.png", "image/png")



with st.spinner(text='In progress'):
   time.sleep(5)
   st.sidebar.success('Done')

st.sidebar.error('Error message')
st.sidebar.warning('Warning message')
st.sidebar.info('Info message')
st.sidebar.success('Success message')

"""
st.balloons()
st.snow()
st.exception(e)
"""
progress_text = "Operation in progress. Please wait."
my_bar = st.sidebar.progress(0, text=progress_text)

for percent_complete in range(100):
    time.sleep(0.1)
    my_bar.progress(percent_complete + 1, text=progress_text)
