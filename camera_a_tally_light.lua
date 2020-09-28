local obs = require 'obslua'
local notifier = require 'obs_change_notifier'

source = 'Camera A'

function script_load(settings)
  notifier.configure({
    source = source,
    active_url = 'http://localhost:8000/A/GREEN',
    inactive_url = 'http://localhost:8000/A/RED',
    heartbeat_interval = 3000
  })
end

function script_description()
  return "Tally light control for " .. source
end
