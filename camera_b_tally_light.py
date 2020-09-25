import obspython as obs
from obs_change_notifier import ObsChangeNotifier

client = ObsChangeNotifier(
             obs=obs,
             watched_source='Camera B',
             base_url='http://10.4.2.13',
             heartbeat_interval=4000
           )

def script_description():
  global client

  return "Tally light management for " + client.watched_source

def script_load(settings):
  global client

  client.connect('source_activate', '/GREEN')
  client.connect('source_deactivate', '/RED')

  client.set_current('/RED')

def script_unload():
  global client

  client.set_current('/RED')
