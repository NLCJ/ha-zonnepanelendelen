"""Platform for sensor integration."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import ENERGY_KILO_WATT_HOUR
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .api import API
from .const import CONST_PASSWORD, CONST_USERNAME


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the sensor platform."""

    # login to API
    zpd_client = API(config[CONST_USERNAME], config[CONST_PASSWORD])
    zpd_client.login()

    # get list of projects invested in
    projects = zpd_client.projects()
    # create sensors per project
    sensors = []
    for project in projects["projects_invested_in"]:
        sensor = ZPDSensor(
            api=zpd_client, project_id=project["id"], project_name=project["name"]
        )
        sensor.api = zpd_client
        sensor.project_id = project["id"]
        sensors.append(sensor)

    add_entities(sensors)


class ZPDSensor(SensorEntity):
    """Representation of a Sensor."""

    api: API
    project_id: int

    _attr_native_unit_of_measurement = ENERGY_KILO_WATT_HOUR
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, api: API, project_id: int, project_name: str) -> None:
        self.api = api
        self.project_id = project_id
        self._attr_name = "Zonnepanelendelen %s" % project_name

    def update(self) -> None:
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """

        data = self.api.project(self.project_id)
        self._attr_native_value = data["metrics"]["production_all"]["total_power_kWh"]