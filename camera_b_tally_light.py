import obspython as obs
import urllib.request

watched_source = 'Camera B'
base_url = 'http://10.4.2.13'
heartbeat_ms = 4000

def script_description():
  return """
    Tally light management for Camera B.
  """

def camera_activated(obs_calldata):
  signal_receiver(obs_calldata, '/ON')

def camera_deactivated(obs_calldata):
  signal_receiver(obs_calldata, '/OFF')

def signal_receiver(obs_calldata, endpoint, postbody=None):
  global watched_source
  global base_url

  source = obs.calldata_source(obs_calldata, "source")
  source_name = obs.obs_source_get_name(source)

  if source_name == watched_source:
    url = base_url + endpoint
    obs.script_log(obs.LOG_INFO, url)
    make_request(url)

def heartbeat():
  global base_url

  url = base_url + '/HB'
  # obs.script_log(obs.LOG_INFO, url)
  make_request(url)

def make_request(url):
  try:
    urllib.request.urlopen(url, None, 1)
  except urllib.error.URLError as e:
    obs.script_log(obs.LOG_INFO, 'ERROR: ' + url)

# called when properties are updated
def script_load(settings):
  global watched_source
  global heartbeat_ms

  obs.script_log(obs.LOG_INFO, 'now watching ' + watched_source)

  obs_signal_handler = obs.obs_get_signal_handler()

  obs.signal_handler_connect(
    obs_signal_handler,
    'source_activate',
    camera_activated
  )
  obs.signal_handler_connect(
    obs_signal_handler,
    'source_deactivate',
    camera_deactivated
  )

  obs.timer_add(heartbeat, heartbeat_ms)
  obs.script_log(obs.LOG_INFO, 'adding heartbeat timer.')
