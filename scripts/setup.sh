# debug
# set -o xtrace

# VPC Configuration
VPC_CIDR=$(aws ec2 describe-vpcs | jq -r '.Vpcs[0].CidrBlock')
echo "VPC CIDR: $VPC_CIDR"

INSTANCE_ACCESS_SEC_GRP="INSTANCE_ACCESS-`date +'%N'`"

echo "setup firewall $INSTANCE_ACCESS_SEC_GRP"
aws ec2 create-security-group   \
    --group-name $INSTANCE_ACCESS_SEC_GRP       \
    --description "Instances internal communication to instances" 

# figure out my ip
MY_IP=$(curl ipinfo.io/ip)
echo "My IP: $MY_IP"

echo "setup rule allowing SSH access to $MY_IP only"
aws ec2 authorize-security-group-ingress        \
    --group-name $INSTANCE_ACCESS_SEC_GRP --port 22 --protocol tcp \
    --cidr $MY_IP/32


# ELB Configuration
python3 scripts/elb.py


# Add two nodes
source scripts/add_node.sh
