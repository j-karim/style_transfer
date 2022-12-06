instance_ip=104.171.203.21

src_base_dir_1=NeuralStyleTransfer/FastStyleTransfer/images
dst_base_dir_1=~/Documents/pycharm_projects/NeuralStyleTransfer/FastStyleTransfer

src_base_dir_2=NeuralStyleTransfer/FastStyleTransfer/models
dst_base_dir_2=~/Documents/pycharm_projects/NeuralStyleTransfer/FastStyleTransfer

#echo ubuntu@$instance_ip:/home/ubuntu/$src_base_dir_1   #$dst_base_dir_1
rsync -av ubuntu@$instance_ip:/home/ubuntu/$src_base_dir_1 $dst_base_dir_1
#
#echo ubuntu@$instance_ip:/home/ubuntu/$src_base_dir_2/* ~/$dst_base_dir_2
rsync -av --exclude '**/*vgg16*' --include '**/*/checkpoint_2*' --exclude '**/*/checkpoint_*' ubuntu@$instance_ip:/home/ubuntu/$src_base_dir_2 $dst_base_dir_2


