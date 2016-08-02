# -*- mode: ruby -*-
# vi: set ft=ruby :
# Vagrant box build around skillachie's 'Ark Agent'
# Added a some useful tools to it like iPython and monitoring for celery and RabbitMQ
#
# JWR, @aug-2016


# Deployment script
$script = <<SCRIPT
apt-get install -y wget vim screen

apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv EA312927
echo "deb http://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.2 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.2.list

wget -O- https://www.rabbitmq.com/rabbitmq-release-signing-key.asc | sudo apt-key add -
echo 'deb http://www.rabbitmq.com/debian/ testing main' | sudo tee /etc/apt/sources.list.d/rabbitmq.list

apt-get update
apt-get install -y --allow-unauthenticated mongodb-org

apt-get install -y --allow-unauthenticated rabbitmq-server
rabbitmq-plugins enable rabbitmq_management
rabbitmqctl add_user admin admin
rabbitmqctl set_permissions -p / admin ".*" ".*" ".*"
rabbitmqctl set_user_tags admin administrator

cat <<EOT >> /lib/systemd/system/mongod.service
[Unit]
Description=High-performance, schema-free document-oriented database
After=network.target
Documentation=https://docs.mongodb.org/manual

[Service]
User=mongodb
Group=mongodb
ExecStart=/usr/bin/mongod --quiet --config /etc/mongod.conf

[Install]
WantedBy=multi-user.target
EOT
service mongod start

# Install Python environment
apt-get install -y python-pip
pip install --upgrade pip

pip install celery pymongo ystockquote finsymbols pyyaml flower jupyter

# Create indexes
bash /vagrant/ark_agent/setup_mongo_indices.sh >/dev/null

# Setup screen environment as user vagrant
sudo su - vagrant <<'VAGRANT'
cat <<EOTSCREEN >> ~/.screenrc
defscrollback 10000
startup_message off
attrcolor b ".I"
termcapinfo xterm 'Co#256:AB=\E[48;5;%dm:AF=\E38;5;%dm'
termcapinfo xterm* ti@:te@
defbce "on"
EOTSCREEN

screen -AdmS stack -t Bash bash -c "bash"
sleep 2
screen -S stack -X screen -t Jupyter bash -c "jupyter notebook --no-browser --ip 0.0.0.0 --port 8888; bash"
sleep 2
screen -S stack -X screen -t Flower bash -c "celery flower --broker=amqp://guest:guest@localhost:5672//; bash"
sleep 2
cd /vagrant
screen -S stack -X screen -t Celery bash -c "cd /vagrant; sudo C_FORCE_ROOT=true celery worker --app ark_agent -l info -E -B; bash"
sleep 2
VAGRANT
SCRIPT

# Vagrant setup
Vagrant.configure("2") do |config|
  config.vm.hostname = "ark-agent"
  config.vm.box = "bento/ubuntu-16.04"
  config.vm.provision "shell", inline: $script

  # MongoDB
  config.vm.network :forwarded_port, guest: 27017, host: 27017

  # Celery flower
  config.vm.network :forwarded_port, guest: 5555, host: 5555

  #RabbitMQ
  config.vm.network :forwarded_port, guest: 5672, host: 5672
  config.vm.network :forwarded_port, guest: 15672, host: 15672

  # iPython notebook server
  config.vm.network :forwarded_port, guest: 8888, host: 8888
end
