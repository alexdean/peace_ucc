import obspython as obs
from obs_change_notifier import OBSChangeNotifier

client = OBSChangeNotifier(
           obs=obs,
           watched_source='Camera B',
           base_url='http://10.4.2.13'
         )

def script_description():
  global client

  return "Tally light management for " + client.watched_source

def script_load(settings):
  global client

  client.connect('source_activate', '/GREEN')
  client.connect('source_deactivate', '/RED')
  client.set_current('/RED')
  client.begin_heartbeats(interval=3000)

def script_unload():
  global client

  client.set_current('/RED')
