# Update package manager
sudo apt update
# Setup AWS CLI
sudo apt install awscli zip
# Install pypi
sudo apt-get install python3-pip -y
# Install boto3
sudo pip install boto3
# Install boto3
sudo pip3 install --upgrade awscli
# Setup jq
sudo apt-get install jq
# Configure AWS setup (keys, region, etc)
aws configure