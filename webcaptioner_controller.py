import obspython as obs
from obs_change_notifier import OBSChangeNotifier

client = OBSChangeNotifier(
           obs=obs,
           watched_source='Captions Enabled',
           base_url='http://localhost:4567'
         )

def script_description():
  global client

  return "Subtitle management for " + client.watched_source

def script_load(settings):
  global client

  client.connect('source_activate', '/control', {'enabled': 'true'})
  client.connect('source_deactivate', '/control', {'enabled': 'false'})
