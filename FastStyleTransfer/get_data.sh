# shellcheck disable=SC2164

apt install pip
pip install Pillow -U

mkdir dataset
mkdir models

cd dataset

wget http://images.cocodataset.org/zips/train2014.zip

unzip -qq train2014.zip

