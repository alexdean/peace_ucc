import urllib.request

# watch a given source in OBS, and notify an HTTP service when OBS emits signals
# related to that source.
#
# @example: When source 'Camera A' is made live, a GET request will be sent to http://192.168.1.10/LIVE.
#
#   notifier = ObsChangeNotifier(watched_source='Camera A', base_url='http://192.168.1.10')
#   notifier.connect('source_activate', '/LIVE')
class OBSChangeNotifier:
  def __init__(self, obs, watched_source, base_url, heartbeat_interval):
    self.obs = obs
    # self.obs.script_log(self.obs.LOG_INFO, '__init__()')
    self.watched_source = watched_source
    self.base_url = base_url
    # self.heartbeat_endpoint = None
    # self.heartbeat_every = float('inf')
    # self.last_updated_at = time.time()
    self.signal_handler_data = []
    self.heartbeat_interval = heartbeat_interval
    self.current_endpoint = None
    self.obs.timer_add(self.send_heartbeat, heartbeat_interval)

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
  def connect(self, obs_signal, endpoint):
    obs_signal_handler = self.obs.obs_get_signal_handler()
    callback = (lambda obs_calldata: self.signal_receiver(obs_calldata, endpoint))

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

  # invoked on a timer. repeatedly ping the current endpoint.
  #
  # arduino device is configured to cease displaying any indicator if the flow
  # of pings ceases. prevents false readings if OBS exits or if network
  # connectivity is interrupted.
  def send_heartbeat(self):
    # self.obs.script_log(self.obs.LOG_DEBUG, 'send_heartbeat()')
    if self.current_endpoint != None:
      self.send_update(self.current_endpoint)

  # receive a signal from OBS.
  #
  # if the emitted source matches the source we are tracking,
  # update the endpoint we're currently pinging.
  def signal_receiver(self, obs_calldata, endpoint):
    source = self.obs.calldata_source(obs_calldata, "source")
    source_name = self.obs.obs_source_get_name(source)

    if source_name == self.watched_source:
      self.set_current(endpoint)

  # unconditionally set which endpoint we are currently pinging
  def set_current(self, endpoint):
    self.current_endpoint = endpoint
    self.send_update(endpoint)

  # make an HTTP request for the specified endpoint
  def send_update(self, endpoint):
    url = self.base_url + endpoint

    try:
      urllib.request.urlopen(url, None, 1)
    except urllib.error.URLError as e:
      self.obs.script_log(self.obs.LOG_INFO, 'ERROR: ' + url)

    # self.obs.script_log(self.obs.LOG_DEBUG, 'send_update: ' + endpoint)
