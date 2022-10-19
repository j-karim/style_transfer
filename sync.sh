src_base_dir=~/Documents/pycharm_projects/NeuralStyleTransfer
dst_base_dir=NeuralStyleTransfer
instance_ip=104.171.203.223

echo $src_base_dir/* ubuntu@$instance_ip:~/$dst_base_dir
rsync -av --exclude 'FastStyleTransfer/models' --exclude 'FastStyleTransfer/images/out' $src_base_dir/* ubuntu@$instance_ip:$dst_base_dir

ssh ubuntu@$instance_ip chmod +x /home/ubuntu/NeuralStyleTransfer/FastStyleTransfer/train.py
echo chmod +x /home/ubuntu/NeuralStyleTransfer/FastStyleTransfer/train.py
exit

