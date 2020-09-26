import urllib.request
import socket
from datetime import datetime

# watch a given source in OBS, and notify an HTTP service when OBS emits signals
# related to that source.
#
# @example: When source 'Camera A' is made live, a GET request will be sent to http://192.168.1.10/LIVE.
#
#   notifier = ObsChangeNotifier(watched_source='Camera A', base_url='http://192.168.1.10')
#   notifier.connect('source_activate', '/LIVE')
class OBSChangeNotifier:
  def __init__(self, obs, watched_source, base_url):
    self.obs = obs
    self.watched_source = watched_source
    self.base_url = base_url

    self.signal_handler_data = []
    self.current_endpoint = None

  def watched_source(self):
    return self.watched_source

  def disconnect_all(self):
    obs_signal_handler = self.obs.obs_get_signal_handler()

    for data in self.signal_handler_data:
      self.obs.script_log(self.obs.LOG_INFO, 'disconnecting from ' + data['obs_signal'])
      # TODO: this doesn't work. old signal handlers continue to be active even after this is called.
      # https://github.com/obsproject/obs-studio/pull/3286
      self.obs.signal_handler_disconnect(
        obs_signal_handler,
        data['obs_signal'],
        data['callback']
      )

  # connect an obs signal to a remote endpoint which should be requested when
  # the given signal is received.
  def connect(self, obs_signal, endpoint, postbody=None):
    obs_signal_handler = self.obs.obs_get_signal_handler()
    callback = (lambda obs_calldata: self.signal_receiver(obs_calldata, endpoint, postbody))

    data = {
      'obs_signal': obs_signal,
      'callback': callback
    }

    self.signal_handler_data.append(data)

    self.obs.signal_handler_connect(
      obs_signal_handler,
      obs_signal,
      callback
    )

  # create a timer to periodically re-request our current_endpoint
  def begin_heartbeats(self, interval=4000):
    self.obs.timer_add(self.send_heartbeat, interval)

  # invoked on a timer. repeatedly ping the current endpoint.
  #
  # arduino device is configured to cease displaying any indicator if the flow
  # of pings ceases. prevents false readings if OBS exits or if network
  # connectivity is interrupted.
  def send_heartbeat(self):
    if self.current_endpoint != None:
      self.send_update(self.current_endpoint)

  # receive a signal from OBS.
  #
  # if the emitted source matches the source we are tracking,
  # update the endpoint we're currently pinging.
  def signal_receiver(self, obs_calldata, endpoint, postbody=None):
    source = self.obs.calldata_source(obs_calldata, "source")
    source_name = self.obs.obs_source_get_name(source)

    if source_name == self.watched_source:
      self.set_current(endpoint, postbody)

  # unconditionally set which endpoint we are currently pinging
  def set_current(self, endpoint, postbody=None):
    self.current_endpoint = endpoint
    self.send_update(endpoint, postbody)

  # make an HTTP request for the specified endpoint
  def send_update(self, endpoint, postbody=None):
    url = self.base_url + endpoint

    if postbody != None:
      method = 'POST'
      data = urllib.parse.urlencode(postbody).encode()
    else:
      method = 'GET'
      data = None

    try:
      request = urllib.request.Request(url, data=data, method=method)
      urllib.request.urlopen(request, None, 1)
    except (urllib.error.URLError, socket.timeout) as e:
      log(url, 'ERROR')

  # write a message to obs script log
  # always use INFO level to prevent OBS from popping up the script log console
  # (which steals focus and makes it harder to solve whatever is triggering the errors.)
  def log(message, level):
    self.obs.script_log(self.obs.LOG_INFO, datetime.now().strftime('%H:%M:%S.%f') + ' [' + level + '] ' + message)
