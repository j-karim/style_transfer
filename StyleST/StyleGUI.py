import os
import bcrypt
import numpy as np

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
import torch
import FastStyleTransfer.transformer as transformer
import streamlit as st
from pathlib import Path
from PIL import Image

from FastStyleTransfer import utils




def write():
    st.title('Frohe Weihnachten my love! :)')

    password = st.text_input('Input password', type='password')
    if not check_password(password):
        return
    image_blob = st.file_uploader('Upload input photo', type=['png', 'jpg', 'jpeg'])

    models = sorted(get_list_of_models())
    model_key = st.selectbox('Select style', [x.parent.stem for x in models])
    model_path = [x for x in models if x.parent.stem == model_key][0]

    if image_blob is None:
        return
    image = load_image(image_blob)
    st.header('Input image')
    st.image(image)

    style_image = load_style_image(model_key)
    st.header('Style image')
    st.image(style_image)

    device = ("cuda" if torch.cuda.is_available() else "cpu")
    model = load_model(model_path, device)
    stylized_image = infer_image(image, model, device)
    st.header('Stylized image')
    st.image(stylized_image)

    show_present_btn = st.button('Ok reicht jetzt, zeig mir das Geschenk :P')
    if show_present_btn:
        show_present()


@st.cache
def get_list_of_models():
    model_path = Path(__file__).parent.parent / 'FastStyleTransfer' / 'models'
    checkpoint_name = 'checkpoint_20695.pth'
    models = [x / checkpoint_name for x in model_path.glob('*') if x.is_dir() and (x / checkpoint_name).exists()]
    return models


@st.cache
def load_image(image_blob):
    image = Image.open(image_blob)
    return image


@st.cache
def load_style_image(model_key):
    style_img_path = Path(__file__).parent.parent / 'FastStyleTransfer' / 'images'
    style_img_path = list(style_img_path.glob(f'{model_key}*'))[0]
    image = Image.open(style_img_path)

    return image


@st.cache
def load_model(model_path, device):

    # Load Transformer Network
    net = transformer.TransformerNetwork()
    net.load_state_dict(torch.load(str(model_path), map_location=device))
    net = net.to(device)
    return net


@st.cache
def infer_image(image, model, device):

    new_img_width = 600
    new_img_height = new_img_width / image.width * image.height
    image = image.resize((int(new_img_width), int(new_img_height)))
    content_tensor = utils.itot(image).to(device)

    generated_tensor = model(content_tensor)
    generated_image = utils.ttoi(generated_tensor.detach())
    generated_image = np.clip(generated_image / 255.0, 0.0, 1.0)
    return generated_image


def check_password(pw: str):
    encoded_pw = pw.encode()
    salt = b'$2b$12$8iIIIT//hLqNX5ID9Grplu'
    hashed = bcrypt.hashpw(encoded_pw, salt)
    if hashed == b'$2b$12$8iIIIT//hLqNX5ID9GrpluqtskeieRmGGVZy2MPOOhKClZa86Eus.':
        return True
    return False


def show_present():
    st.header('Geschenk')
    st.write('Hey, frohe Weihnachten! :) Ist das Kunst oder kann das weg? Well i don\'t know! Aber das Geschenk ist ......... \n\n\n\n\n\n\n'
            'Kunst. ')


write()
