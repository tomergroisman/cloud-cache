# debug
# set -o xtrace

KEY_NAME="cloud-cache-`date +'%N'`"
KEY_PEM=".pem/$KEY_NAME.pem"
INSTANCE_ACCESS_SEC_GRP=$(aws ec2 describe-security-groups \
    --filters Name=group-name,Values=INSTANCE_ACCESS-* | \
    jq '.SecurityGroups[0].GroupName' | \
    tr -d '"')

echo "create pem directory"
mkdir -p .pem
chmod 775 .pem

echo "create key pair $KEY_PEM to connect to instances and save locally"
aws ec2 create-key-pair --key-name $KEY_NAME \
    | jq -r ".KeyMaterial" > $KEY_PEM

# secure the key pair
chmod 400 $KEY_PEM

UBUNTU_20_04_AMI="ami-05f7491af5eef733a"

echo "Creating Ubuntu 20.04 instance..."
RUN_INSTANCES=$(aws ec2 run-instances   \
    --image-id $UBUNTU_20_04_AMI        \
    --instance-type t3.micro            \
    --key-name $KEY_NAME                \
    --security-groups $INSTANCE_ACCESS_SEC_GRP)

INSTANCE_ID=$(echo $RUN_INSTANCES | jq -r '.Instances[0].InstanceId')

echo "Waiting for instance creation..."
aws ec2 wait instance-running --instance-ids $INSTANCE_ID

PUBLIC_IP=$(aws ec2 describe-instances  --instance-ids $INSTANCE_ID | 
    jq -r '.Reservations[0].Instances[0].PublicIpAddress'
)

echo "New instance $INSTANCE_ID @ $PUBLIC_IP"

echo "add new instance to elb target group"
python3 scripts/elb.py register_instance_in_elb $INSTANCE_ID

echo "deploying code to production"
scp -i $KEY_PEM -o "StrictHostKeyChecking=no" -o "ConnectionAttempts=60" -r ~/.aws src requirements.txt ubuntu@$PUBLIC_IP:/home/ubuntu/

echo "setup production environment"
ssh -i $KEY_PEM -o "StrictHostKeyChecking=no" -o "ConnectionAttempts=10" ubuntu@$PUBLIC_IP <<EOF
    sudo apt update -y
    sudo apt-get install python3-pip -y
    sudo pip install -r requirements.txt
    # run app
    cd src/
    nohup python3 app.py & python3 vpc.py && fg
EOF

echo "done."