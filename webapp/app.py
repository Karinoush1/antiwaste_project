import streamlit as st
from PIL import Image
from io import BytesIO
import base64

st.set_page_config(
    page_title="AntiWaste",
    page_icon="🍅",
    layout="wide"
)

st.write("## Antiwaste application")
st.write("🥑 Try uploading an image. This code is open source and available [antiwaste](https://github.com/cdouadi/antiwaste) on GitHub. 🍅")
st.sidebar.write("## Upload :gear:")
picture = st.sidebar.camera_input("Take a picture")


if picture:
    st.image(picture)


def fix_image(upload):
    image = Image.open(upload)
    col1.write("Original Image :camera:")
    col1.image(image)

    st.sidebar.markdown("\n")


col1, col2 = st.columns(2)
my_upload = st.sidebar.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

if my_upload is not None:
    fix_image(upload=my_upload)

st.download_button("Download fixed image", "fixed.png", "image/png")