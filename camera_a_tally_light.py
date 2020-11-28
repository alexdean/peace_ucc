import obspython as obs
from obs_change_notifier import OBSChangeNotifier

client = OBSChangeNotifier(
           obs=obs,
           watched_source='Camera A',
           base_url='http://localhost:4567/repeater',
           debug_heartbeats=True
         )

def script_description():
  global client

  return "Tally light management for " + client.watched_source

def script_load(settings):
  global client

  client.connect('source_activate', '?key=A&value=GREEN')
  client.connect('source_deactivate', '?key=A&value=RED')
  client.set_current('?key=A&value=RED')

def script_unload():
  global client

  client.set_current('?key=A&value=RED')
