import os

import cv2
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
    st.header('Frohe Weihnachten my love! :)')
    image_blob = st.file_uploader('Upload style photo', type=['png', 'jpg', 'jpeg'])

    models = sorted(get_list_of_models())
    model_key = st.selectbox('Select style model', [x.parent.stem for x in models])
    model_path = [x for x in models if x.parent.stem == model_key][0]

    style_image = load_style_image(model_key)
    st.image(style_image)



    if image_blob is None:
        return
    image = load_image(image_blob)
    st.image(image)


    device = ("cuda" if torch.cuda.is_available() else "cpu")
    model = load_model(model_path, device)
    stylized_image = infer_image(image, model, device)
    st.image(stylized_image)


@st.cache
def get_list_of_models():
    model_path = Path(__file__).parent.parent / 'FastStyleTransfer' / 'models'
    checkpoint_name = 'checkpoint_20695.pth'
    models = [x / checkpoint_name for x in model_path.glob('*') if x.is_dir() and (x / checkpoint_name).exists()]
    return models


@st.cache
def load_image(image_blob):
    image = Image.open(image_blob)
    image = np.asarray(image)
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
    new_img_height = new_img_width / image.shape[1] * image.shape[0]
    image = cv2.resize(image, (int(new_img_width), int(new_img_height)))
    content_tensor = utils.itot(image).to(device)

    generated_tensor = model(content_tensor)
    generated_image = utils.ttoi(generated_tensor.detach())
    generated_image = np.clip(generated_image / 255.0, 0.0, 1.0)
    return generated_image


write()
