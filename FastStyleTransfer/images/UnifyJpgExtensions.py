from pathlib import Path


def main():
    image_list = Path(__file__).parent.glob('*')
    for img_path in image_list:
        if img_path.suffix == '.jpeg':
            new_path = img_path.parent / f'{img_path.stem}.jpg'
            img_path.rename(new_path)


if __name__ == '__main__':
    main()
