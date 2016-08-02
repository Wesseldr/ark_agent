##Vagrant Ark Agent
Distributed Agent used to collect current and historical End Of Day stock data. 
Techniques used:
- Python2.7 (any volunteers for porting this to 3.5 ? ;-)
- Celery
- MongoDB

Based on the excellent work of skillachie http://skillachie.github.io/ark_agent/

Added in this fork:
- RabbitMQ
- RabbitMQ monitoring web interface
- Celery flower for monitoring & managing the celery cluster
- iPython/Jupyter notebook for writing & testing your own code
- Vagrant for wrapping it all up in a single ubuntu-16.04 box

Mathlibs
- numpy
- pandas
- SciPy
- matplotlib

The ark agent is running in a full Vagrant box including the following web services:
- Celery Flower web interface (http://localhost:5555)
- iPhython/Jupyter notebook web interface (http://localhost:8888)
- RabbitMQ-Manager web interface (http://localhost:15672) user: admin pass: admin

###Prerequisite & Setup
- have Vagrant installed (http://www.vagrantup.com)
- Clone this repository

###Setup
run: ``vagrant up``

Every thing will be setup for you. When the creation of the Vagrant ubuntu box is finished, login with:

``vagrant ssh`` and use ``screen -r`` to access the output of: Jupyter, Flower and Celery.

[ctrl-a "] for a list of screens

Don't forget to connect your browser to the web interfaces on port 5555, 8888 and 15672
##Services
#### MongoDB
localhost:27017

#### RabbitMQ
host: localhost  
port: 5672    
username: guest  
password: guest

_composed by JWR, aug-2016_, feel free to clone/fork change/use :-)
