# Update package manager
sudo apt update -y
# Setup AWS CLI
sudo apt install awscli zip -y
# Install pypi
sudo apt install python3-pip -y
# Setup jq
sudo apt-get install jq -y
# Install boto3
sudo pip3 install boto3
# Install boto3
sudo pip3 install --upgrade awscli
# Configure AWS setup (keys, region, etc)
aws configure