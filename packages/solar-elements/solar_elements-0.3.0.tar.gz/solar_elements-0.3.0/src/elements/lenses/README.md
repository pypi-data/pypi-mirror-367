# Lenses

Lenses are essentially plugin systems for building application
state according to the core event log.

A lens will generally define a number of `actions`, which are
functions that map events into some sort of state change within
the core.

It may also attach accessor functions to the core state so that
data can be easily embedded into templates.
