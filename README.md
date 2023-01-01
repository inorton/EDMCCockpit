# EDMC Cockpit 
(c) 2023 Ian Norton

This is a plugin for [EDMC](https://github.com/EDCD/EDMarketConnector) 
that adds webserver and websocket support using 
[Flask](https://flask.palletsprojects.com/en/2.2.x/) and several other
packages.

<a href="https://youtu.be/nupqTuMcND0" target="_blank">
  <img src="http://img.youtube.com/vi/nupqTuMcND0/mqdefault.jpg" 
   alt="Watch the EDMC Cockpit video" width="320" height="200" />
</a>

Each "Module" is a[Flask Blueprint](https://flask.palletsprojects.com/en/2.2.x/blueprints/), 
so it should be _easy_ to add more as the need arises.

## Modules
Over time this list will grow! Please submit requests for new module 
ideas!

### Fuel Manager

This is probably the most useful module (so far). Shows the current fuel tank and scoop performance as well as which stars 
on a plotted route are scoopable. If you are scooping it will also give 
you a real-time estimate for how long until your tanks are full.

### Raw Journal and Status

Not _very_ useful but still a good example of how to write a simple module using
the websocket interface. They simply repeat the journal or status events from EDMC 
into a websocket that is read via events in javascript.

## Compatibility

Note: The plugin ships its own copies of flask and several other plugins so
may introduce problems if other plugins you use depend on different versions of the
same ones. Please see [packages/README.txt](https://github.com/inorton/EDMCCockpit/blob/main/packages/README.txt) for
more info.