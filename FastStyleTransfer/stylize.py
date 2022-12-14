import torch
import utils
import transformer
import os
from torchvision import transforms
import time
import cv2

STYLE_TRANSFORM_PATH = "models/picasso_1/checkpoint_20695.pth"
# STYLE_TRANSFORM_PATH = "transforms/tokyo_ghoul.pth"
# PRESERVE_COLOR = False


def stylize(style_transform_path, preserve_color=False):
    # Device
    device = ("cuda" if torch.cuda.is_available() else "cpu")

    # Load Transformer Network
    net = transformer.TransformerNetwork()
    net.load_state_dict(torch.load(style_transform_path, map_location=device))
    net = net.to(device)

    with torch.no_grad():
        torch.cuda.empty_cache()
        print("Stylize Image~ Press Ctrl+C and Enter to close the program")
        content_image_path = r'images/up-diliman.jpg'
        # content_image_path = r'/Users/janekbecker/Pictures/20180305_172930.jpeg'  # input("Enter the image path: ")
        content_image_path = r'/Users/janekbecker/Pictures/DSCF0626.jpeg'  # input("Enter the image path: ")
        content_image = utils.load_image(content_image_path)
        content_image = cv2.resize(content_image, (600, 400))
        starttime = time.time()
        content_tensor = utils.itot(content_image).to(device)
        generated_tensor = net(content_tensor)
        generated_tensor = torch.concat([content_tensor, generated_tensor], dim=2)
        generated_image = utils.ttoi(generated_tensor.detach())
        if preserve_color:
            generated_image = utils.transfer_color(content_image, generated_image)
        print("Transfer Time: {}".format(time.time() - starttime))

        utils.show(generated_image)
        # utils.saveimg(generated_image, "helloworld.jpg")
        return generated_image


def stylize_folder_single(style_path, content_folder, save_folder, preserve_color=False):
    """
    Reads frames/pictures as follows:

    content_folder
        pic1.ext
        pic2.ext
        pic3.ext
        ...

    and saves as the styled images in save_folder as follow:

    save_folder
        pic1.ext
        pic2.ext
        pic3.ext
        ...
    """
    # Device
    device = ("cuda" if torch.cuda.is_available() else "cpu")

    # Load Transformer Network
    net = transformer.TransformerNetwork()
    net.load_state_dict(torch.load(style_path))
    net = net.to(device)

    # Stylize every frame
    images = [img for img in os.listdir(content_folder) if img.endswith(".jpg")]
    with torch.no_grad():
        for image_name in images:
            # Free-up unneeded cuda memory
            torch.cuda.empty_cache()

            # Load content image
            content_image = utils.load_image(content_folder + image_name)
            content_tensor = utils.itot(content_image).to(device)

            # Generate image
            generated_tensor = net(content_tensor)
            generated_image = utils.ttoi(generated_tensor.detach())
            if preserve_color:
                generated_image = utils.transfer_color(content_image, generated_image)
            # Save image
            utils.saveimg(generated_image, save_folder + image_name)


def stylize_folder(style_path, folder_containing_the_content_folder, save_folder, batch_size=1):
    """Stylizes images in a folder by batch
    If the images  are of different dimensions, use transform.resize() or use a batch size of 1
    IMPORTANT: Put content_folder inside another folder folder_containing_the_content_folder

    folder_containing_the_content_folder
        content_folder
            pic1.ext
            pic2.ext
            pic3.ext
            ...

    and saves as the styled images in save_folder as follow:

    save_folder
        pic1.ext
        pic2.ext
        pic3.ext
        ...
    """
    # Device
    device = ("cuda" if torch.cuda.is_available() else "cpu")

    # Image loader
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Lambda(lambda x: x.mul(255))
    ])
    image_dataset = utils.ImageFolderWithPaths(folder_containing_the_content_folder, transform=transform)
    image_loader = torch.utils.data.DataLoader(image_dataset, batch_size=batch_size)

    # Load Transformer Network
    net = transformer.TransformerNetwork()
    net.load_state_dict(torch.load(style_path))
    net = net.to(device)

    # Stylize batches of images
    with torch.no_grad():
        for content_batch, _, path in image_loader:
            # Free-up unneeded cuda memory
            torch.cuda.empty_cache()

            # Generate image
            generated_tensor = net(content_batch.to(device)).detach()

            # Save images
            for i in range(len(path)):
                generated_image = utils.ttoi(generated_tensor[i])
                # if (PRESERVE_COLOR):
                #     generated_image = utils.transfer_color(content_image, generated_image)  # todo what about this ?
                image_name = os.path.basename(path[i])
                utils.saveimg(generated_image, save_folder + image_name)


if __name__ == '__main__':
    stylize(STYLE_TRANSFORM_PATH)
