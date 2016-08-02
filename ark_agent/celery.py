from __future__ import absolute_import
from celery.schedules import crontab
from celery import Celery
import os
import yaml

module_path = os.path.dirname(os.path.realpath(__file__))
config_dir = os.path.join(module_path,'configs')
file_path = os.path.abspath(config_dir) + os.sep + 'mongo_settings.yaml'
config_file = open(file_path,'r')
config_data = yaml.load(config_file)

BACKEND_URL = "mongodb://%s:%d/jobs" %(config_data['hostname'],config_data['port'])
BROKER_URL = 'amqp://guest:guest@localhost:5672//'

#Loads settings for Backend to store results of jobs
celery = Celery('ark_agent.celery',
		broker=BROKER_URL,
		backend=BACKEND_URL,
		include=['ark_agent.stock_eod_data'])  #list of modules to import when Celery starts


#Schedule Config
celery.conf.update(CELERYBEAT_SCHEDULE = {
                        'every-day-at-seven': {
                        'task': 'ark_agent.stock_eod_data.generate_eod_tasks',
                        'schedule': crontab(minute=00, hour=19),
                                        },
                    },
                    CELERY_TIMEZONE = 'US/Eastern',
                    CELERY_ACCEPT_CONTENT = ['pickle', 'json']
                    )

if __name__ == '__main__':
	celery.start()
