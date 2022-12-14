#! /usr/bin/python
#
import os

import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import random
import numpy as np
import time

from tqdm import tqdm
from pathlib import Path

import vgg
import transformer
import utils

# GLOBAL SETTINGS
TRAIN_IMAGE_SIZE = 256
DATASET_PATH = "dataset"
NUM_EPOCHS = 1
STYLE_IMAGE_PATHS = [
    # "images/van_gogh_1.jpg",
    # "images/asterix.jpg",
    "images/dali_4.jpg",
    "images/dali_5.jpg",
    "images/dali_6.jpg",
    "images/dali_7.jpg",
    "images/dali_8.jpg",
    "images/dali_9.jpg",
    "images/gta.jpg",
    "images/hongkong.jpg",
    "images/imperialist.jpg",
    "images/kahlo_1.jpg",
    "images/kandinsky_1.jpg",
    "images/picasso_1.jpg",
    "images/van_gogh_1.jpg",
    "images/van_gogh_2.jpg",
]
BATCH_SIZE = 4
CONTENT_WEIGHT = 17  # 17
STYLE_WEIGHT = 50  # 25
ADAM_LR = 0.001
SAVE_MODEL_PATH = "models/"
SAVE_IMAGE_PATH = "images/out/"
SAVE_MODEL_EVERY = 500  # 2,000 Images with batch size 4
SEED = 35
PLOT_LOSS = 1


def train(style_path):
    save_model_path = str(Path(SAVE_MODEL_PATH) / Path(style_path).stem) + '/'
    os.makedirs(save_model_path, exist_ok=True)
    save_image_path = str(Path(SAVE_IMAGE_PATH) / Path(style_path).stem) + '/'
    os.makedirs(save_image_path, exist_ok=True)

    # Seeds
    torch.manual_seed(SEED)
    torch.cuda.manual_seed(SEED)
    np.random.seed(SEED)
    random.seed(SEED)

    # Device
    device = ("cuda" if torch.cuda.is_available() else "cpu")

    # Dataset and Dataloader
    transform = transforms.Compose([
        transforms.Resize(TRAIN_IMAGE_SIZE),
        transforms.CenterCrop(TRAIN_IMAGE_SIZE),
        transforms.ToTensor(),
        transforms.Lambda(lambda x: x.mul(255))
    ])
    train_dataset = datasets.ImageFolder(DATASET_PATH, transform=transform)
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)

    # Load networks
    transformer_network = transformer.TransformerNetwork().to(device)
    vgg_net = vgg.VGG16().to(device)

    # Get Style Features
    imagenet_neg_mean = torch.tensor([-103.939, -116.779, -123.68], dtype=torch.float32).reshape(1, 3, 1, 1).to(device)
    style_image = utils.load_image(style_path)
    style_tensor = utils.itot(style_image).to(device)
    style_tensor = style_tensor.add(imagenet_neg_mean)
    b, c, h, w = style_tensor.shape
    style_features = vgg_net(style_tensor.expand([BATCH_SIZE, c, h, w]))
    style_gram = {}
    for key, value in style_features.items():
        style_gram[key] = utils.gram(value)

    # Optimizer settings
    optimizer = optim.Adam(transformer_network.parameters(), lr=ADAM_LR)

    # Loss trackers
    content_loss_history = []
    style_loss_history = []
    total_loss_history = []
    batch_content_loss_sum = 0
    batch_style_loss_sum = 0
    batch_total_loss_sum = 0

    # Optimization/Training Loop
    batch_count = 1
    start_time = time.time()
    for epoch in range(NUM_EPOCHS):
        print("========Epoch {}/{}========".format(epoch + 1, NUM_EPOCHS))
        for content_batch, _ in tqdm(train_loader, total=len(train_loader), desc=f'Epoch {epoch}'):
            # Get current batch size in case of odd batch sizes
            curr_batch_size = content_batch.shape[0]

            # Free-up unneeded cuda memory
            torch.cuda.empty_cache()

            # Zero-out Gradients
            optimizer.zero_grad()

            # Generate images and get features
            content_batch = content_batch[:, [2, 1, 0]].to(device)
            generated_batch = transformer_network(content_batch)
            content_features = vgg_net(content_batch.add(imagenet_neg_mean))
            generated_features = vgg_net(generated_batch.add(imagenet_neg_mean))

            # Content Loss
            mse_loss = nn.MSELoss().to(device)
            content_loss = CONTENT_WEIGHT * mse_loss(generated_features['relu2_2'], content_features['relu2_2'])
            batch_content_loss_sum += content_loss

            # Style Loss
            style_loss = 0
            for key, value in generated_features.items():
                s_loss = mse_loss(utils.gram(value), style_gram[key][:curr_batch_size])
                style_loss += s_loss
            style_loss *= STYLE_WEIGHT
            batch_style_loss_sum += style_loss.item()

            # Total Loss
            total_loss = content_loss + style_loss
            batch_total_loss_sum += total_loss.item()

            # Backprop and Weight Update
            total_loss.backward()
            optimizer.step()

            # Save Model and Print Losses
            if ((batch_count - 1) % SAVE_MODEL_EVERY == 0) or (batch_count == NUM_EPOCHS * len(train_loader)):
                # Print Losses
                print("========Iteration {}/{}========".format(batch_count, NUM_EPOCHS * len(train_loader)))
                print("\tContent Loss:\t{:.2f}".format(batch_content_loss_sum / batch_count))
                print("\tStyle Loss:\t{:.2f}".format(batch_style_loss_sum / batch_count))
                print("\tTotal Loss:\t{:.2f}".format(batch_total_loss_sum / batch_count))
                print("Time elapsed:\t{} seconds".format(time.time() - start_time))

                # Save Model
                checkpoint_path = save_model_path + "checkpoint_" + str(batch_count - 1) + ".pth"
                torch.save(transformer_network.state_dict(), checkpoint_path)
                print("Saved TransformerNetwork checkpoint file at {}".format(checkpoint_path))

                # Save sample generated image
                sample_tensor = generated_batch[0].clone().detach().unsqueeze(dim=0)
                sample_image = utils.ttoi(sample_tensor.clone().detach())
                sample_image_path = save_image_path + "sample0_" + str(batch_count - 1) + ".png"
                utils.saveimg(sample_image, sample_image_path)
                print("Saved sample tranformed image at {}".format(sample_image_path))

                # Save loss histories
                content_loss_history.append(batch_total_loss_sum / batch_count)
                style_loss_history.append(batch_style_loss_sum / batch_count)
                total_loss_history.append(batch_total_loss_sum / batch_count)

            # Iterate Batch Counter
            batch_count += 1

    stop_time = time.time()
    # Print loss histories
    print("Done Training the Transformer Network!")
    print("Training Time: {} seconds".format(stop_time - start_time))
    print("========Content Loss========")
    print(content_loss_history)
    print("========Style Loss========")
    print(style_loss_history)
    print("========Total Loss========")
    print(total_loss_history)

    # Save TransformerNetwork weights
    transformer_network.eval()
    transformer_network.cpu()
    final_path = save_model_path + "transformer_weight.pth"
    print("Saving TransformerNetwork weights at {}".format(final_path))
    torch.save(transformer_network.state_dict(), final_path)
    print("Done saving final model")

    # Plot Loss Histories
    if PLOT_LOSS:
        utils.plot_loss_hist(content_loss_history, style_loss_history, total_loss_history)


for style_image_path in STYLE_IMAGE_PATHS:
    try:
        train(style_image_path)
    except Exception as e:
        print(e)
