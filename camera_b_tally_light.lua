local obs = require 'obslua'
local notifier = require 'obs_change_notifier'

source = 'Camera B'

function script_load(settings)
  notifier.configure({
    source = source,
    active_url = 'http://localhost:8000/B/GREEN',
    inactive_url = 'http://localhost:8000/B/RED',
    heartbeat_interval = 3000
  })
end

function script_description()
  return "Tally light control for " .. source
end
