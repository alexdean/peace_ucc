import obspython as obs
from obs_change_notifier import OBSChangeNotifier

client = OBSChangeNotifier(
           obs=obs,
           watched_source='Camera B',
           base_url='http://localhost:4567/repeater',
           debug_heartbeats=True
         )

def script_description():
  global client

  return "Tally light management for " + client.watched_source

def script_load(settings):
  global client

  client.connect('source_activate', '?key=B&value=GREEN')
  client.connect('source_deactivate', '?key=B&value=RED')
  client.set_current('?key=B&value=RED')

def script_unload():
  global client

  client.set_current('?key=A&value=RED')
