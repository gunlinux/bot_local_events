import os
from dotenv import load_dotenv

load_dotenv()


# fstream

rabbit_url: str = os.environ.get('RABBIT_URL', 'amqp://user:password@localhost:5672/')
rabbit_vhost: str = os.environ.get('RABBIT_VHOST', 'gunlinux_bot')
rabbit_exchange: str = os.environ.get('RABBIT_EXCHANGE', 'twitch_getter')


# QUEUES
LOCAL_EVENTS = 'local_events'


# OBS

obs_password: str = os.environ.get('OBS_PASSWORD', 'BDmkzIIRMNbTRsHB')

# shell

scripts_path: str = os.environ.get('SCRIPT_PATH', '/Users/loki/scripts/')
