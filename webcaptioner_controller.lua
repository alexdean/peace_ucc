local obs = require 'obslua'
local notifier = require 'obs_change_notifier'

source = 'Captions Enabled'

function script_load(settings)
  notifier.configure({
    source = source,
    active_url = {'http://localhost:4567/control', {enabled = 'true'}},
    inactive_url = {'http://localhost:4567/control', {enabled = 'false'}}
  })
end

function script_description()
  return "Subtitle management for " .. source
end
