local export = {}
local obs = require 'obslua'
local curl = require 'lcurl.safe'

watched_source = ''
current_url = ''

function export.configure(config)
  watched_source = config['source']

  if config['active_url'] then
    export.connect('source_activate', config['active_url'])
  end

  if config['inactive_url'] then
    export.connect('source_deactivate', config['inactive_url'])
  end

  -- set up timer to repeatedly request the current_url
  if config['heartbeat_interval'] then
    func = function()
      if current_url ~= '' then
        export.http_request(current_url)
      end
    end

    obs.timer_add(func, config['heartbeat_interval'])
  end

  -- init current_url
  source = obs.obs_get_source_by_name(config['source'])
  is_active = obs.obs_source_active(source)

  if is_active then
    current_url = config['active_url']
    export.http_request(current_url)
  else
    current_url = config['inactive_url']
    export.http_request(current_url)
  end

  obs.obs_source_release(source)
end

function export.connect(event_name, url)
  handler_func = function(obs_calldata)
    source = obs.calldata_source(obs_calldata, "source")
    source_name = obs.obs_source_get_name(source)

    if source_name == watched_source then
      current_url = url
      export.http_request(url)
    end
  end

  obs_signal_handler = obs.obs_get_signal_handler()

  obs.signal_handler_connect(
    obs_signal_handler,
    event_name,
    handler_func
  )
end

function export.http_request(url)
  url_type = type(url)
  if url_type == 'string' then
    export.http_get(url)
  elseif url_type == 'table' then
    export.http_post(url[1], url[2])
  else
    error('unable to make request. url is of type ' .. url_type)
  end
end

function export.http_get(url)
  req = curl.easy{url = url}
  if req:perform() then
    req:close()
  else
    obs.script_log(obs.LOG_INFO, watched_source .. ': GET error.')
  end
end

function export.http_post(url, params)
  req = curl.easy()
  req:setopt_url(url)

  form = curl.form()
  for key, value in pairs(params)
  do
    form:add_content(key, value)
  end

  req:setopt_httppost(form)

  if req:perform() then
    req:close()
  else
    obs.script_log(obs.LOG_INFO, watched_source .. ': POST error.')
  end
end

return export
