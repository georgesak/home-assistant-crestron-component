"""Platform for Crestron Media Player integration."""

from homeassistant.components.media_player import (MediaPlayerEntity ,
    SUPPORT_SELECT_SOURCE,
    SUPPORT_TURN_OFF,
    SUPPORT_TURN_ON,
    SUPPORT_VOLUME_MUTE,
    SUPPORT_VOLUME_SET)

import logging

DOMAIN='crestron'

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    hub = hass.data[DOMAIN]['hub']
    entity = [CrestronRoom(hub, config)]
    async_add_entities(entity)

class CrestronRoom(MediaPlayerEntity):

    def __init__(self, hub, config):
        self._hub = hub
        self._name = config['name']
        self._device_class = "speaker"
        self._supported_features = SUPPORT_SELECT_SOURCE | SUPPORT_VOLUME_MUTE | SUPPORT_VOLUME_SET
        self._mute_join = config['mute_join']
        self._source_number_join = config['source_number_join']
        self._source_list = config['source_list']

    async def async_added_to_hass(self):
        self._hub.register_callback(self.async_write_ha_state)

    async def async_will_remove_from_hass(self):
        self._hub.remove_callback(self.async_write_ha_state)

    @property
    def available(self):
        return self._hub.is_available()

    @property
    def name(self):
        return self._name

    @property
    def should_poll(self):
        return False

    @property
    def device_class(self):
        return self._device_class

    @property
    def supported_features(self):
        return self._supported_features

    @property
    def source_list(self):
        self._source_list.values()

    @property
    def source(self):
         source_num = self._hub.get_analog(self._source_number_join)
         return self._source_list[source_num]

    @property
    def is_volume_muted(self):
         return self._hub.get_digital(self._mute_join)

    @property
    def volume_level(self):
         return self._hub.get_analog(self._volume_join)/65535

    async def async_mute_volume(self, mute):
        self._hub.set_digital(self._mute_join, mute)

    async def async_set_volume_level(self, volume):
        self._hub.set_analog(self._volume_join, int(volume*65535))

    async def async_select_source(self, source):
        for k,v in self._source_list:
            if v == source:
                self._hub.set_analog(self._source_number_join, k)