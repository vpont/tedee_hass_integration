import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.core import callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from pytedee_async import TedeeClientException

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    entities.extend([TedeeUnlatchButton(lock, coordinator) for lock in coordinator.data.values()])
    entities.extend([TedeeUnlockUnlatchButton(lock, coordinator) for lock in coordinator.data.values()])
    async_add_entities(entities)

class TedeeUnlatchButton(CoordinatorEntity, ButtonEntity):
    """Button to only pull the spring (does not unlock if locked)"""
    def __init__(self, lock, coordinator):
        _LOGGER.debug("Setting up ButtonEntity for %s", lock.name)
        super().__init__(coordinator)
        self._lock = lock
        self._attr_has_entity_name = True
        self._attr_name = "Unlatch"
        self._attr_unique_id = f"{lock.id}-unlatch-button"

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._lock.id)},
            name=self._lock.name,
            manufacturer="tedee",
            model=self._lock.type
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._lock = self.coordinator.data[self._lock.id]
        self.async_write_ha_state()
        

    async def async_press(self, **kwargs) -> None:
        try:
            await self.coordinator._tedee_client.pull(self._lock.id)
        except (TedeeClientException, Exception) as ex:
            _LOGGER.debug("Error while unlatching the door through button: %s", ex)
            raise HomeAssistantError(ex) from ex
        

class TedeeUnlockUnlatchButton(CoordinatorEntity, ButtonEntity):
    """Button to unlock and pull the spring / only pull the spring if unlocked"""
    def __init__(self, lock, coordinator):
        _LOGGER.debug("Setting up ButtonEntity for %s", lock.name)
        super().__init__(coordinator)
        self._lock = lock
        self._attr_has_entity_name = True
        self._attr_name = "Unlock & Unlatch"
        self._attr_unique_id = f"{lock.id}-unlockunlatch-button"

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._lock.id)},
            name=self._lock.name,
            manufacturer="tedee",
            model=self._lock.type
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._lock = self.coordinator.data[self._lock.id]
        self.async_write_ha_state()
        

    async def async_press(self, **kwargs) -> None:
        try:
            await self.coordinator._tedee_client.open(self._lock.id)
        except (TedeeClientException, Exception) as ex:
            _LOGGER.debug("Error while opening the door through button: %s", ex)
            raise HomeAssistantError(ex) from ex