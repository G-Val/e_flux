  from homeassistant.components.sensor import SensorEntity
  from homeassistant.core import callback
  from homeassistant.helpers.update_coordinator import CoordinatorEntity

  async def async_setup_entry(hass, entry, async_add_devices):
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id] # Coordinator ophalen
    async_add_devices([EFluxLastSessionEnergy(coordinator)])

  class EFluxLastSessionEnergy(CoordinatorEntity, SensorEntity):

    def __init__(self, coordinator):
      """Initialize the sensor."""
      super().__init__(coordinator) # Belangrijk!

    # ... rest van je sensor code ...
    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data["last_session_energy"] # Gebruik de data