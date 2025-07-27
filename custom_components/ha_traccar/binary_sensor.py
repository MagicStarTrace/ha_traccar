"""Support for ha_traccar binary sensors."""
from __future__ import annotations

import re
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import TraccarServerCoordinator
from .entity import TraccarServerEntity, generate_entity_id


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up binary sensor entities."""
    coordinator: TraccarServerCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = []
    for device_entry in coordinator.data.values():
        device = device_entry["device"]
        device_name = device["name"]
        # 处理设备名称，转换为有效的实体ID格式
        device_id = re.sub(r'[^\w\s]', '', device_name.lower()).replace(" ", "_")
        
        # 创建运动传感器
        motion_sensor = TraccarServerMotionBinarySensor(coordinator, device)
        motion_sensor.entity_id = f"binary_sensor.{device_id}_motion"
        entities.append(motion_sensor)
        
        # 创建状态传感器
        status_sensor = TraccarServerStatusBinarySensor(coordinator, device)
        status_sensor.entity_id = f"binary_sensor.{device_id}_status"
        entities.append(status_sensor)
        
        # 创建充电传感器
        charging_sensor = TraccarServerChargingBinarySensor(coordinator, device)
        charging_sensor.entity_id = f"binary_sensor.{device_id}_charging"
        entities.append(charging_sensor)
    
    async_add_entities(entities)


class TraccarServerMotionBinarySensor(TraccarServerEntity, BinarySensorEntity):
    """Represent a motion binary sensor."""

    _attr_device_class = BinarySensorDeviceClass.MOTION

    def __init__(self, coordinator: TraccarServerCoordinator, device: dict) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, device)
        self._attr_unique_id = f"{self._device_id}_motion"
        self._attr_name = f"{device['name']} 运动"
    
    @property
    def entity_id(self) -> str:
        """Return the entity ID."""
        device_id = re.sub(r'[^\w\s]', '', self._device_name.lower()).replace(" ", "_")
        return f"binary_sensor.{device_id}_motion"
        
    @entity_id.setter
    def entity_id(self, entity_id: str) -> None:
        """Set the entity ID."""
        self._entity_id = entity_id

    @property
    def is_on(self) -> bool:
        """Return true if the binary sensor is on."""
        return self.traccar_position["attributes"].get("motion", False)


class TraccarServerStatusBinarySensor(TraccarServerEntity, BinarySensorEntity):
    """Represent a status binary sensor."""

    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_icon = "mdi:access-point"

    def __init__(self, coordinator: TraccarServerCoordinator, device: dict) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, device)
        self._attr_unique_id = f"{self._device_id}_status"
        self._attr_name = f"{device['name']} 在线"
    
    @property
    def entity_id(self) -> str:
        """Return the entity ID."""
        device_id = re.sub(r'[^\w\s]', '', self._device_name.lower()).replace(" ", "_")
        return f"binary_sensor.{device_id}_status"
        
    @entity_id.setter
    def entity_id(self, entity_id: str) -> None:
        """Set the entity ID."""
        self._entity_id = entity_id

    @property
    def is_on(self) -> bool:
        """Return true if the binary sensor is on."""
        return self.traccar_device["status"] == "online"


class TraccarServerChargingBinarySensor(TraccarServerEntity, BinarySensorEntity):
    """Represent a charging binary sensor."""

    _attr_device_class = BinarySensorDeviceClass.BATTERY_CHARGING
    _attr_icon = "mdi:battery-charging"

    def __init__(self, coordinator: TraccarServerCoordinator, device: dict) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, device)
        self._attr_unique_id = f"{self._device_id}_charging"
        self._attr_name = f"{device['name']} 充电"
    
    @property
    def entity_id(self) -> str:
        """Return the entity ID."""
        device_id = re.sub(r'[^\w\s]', '', self._device_name.lower()).replace(" ", "_")
        return f"binary_sensor.{device_id}_charging"
        
    @entity_id.setter
    def entity_id(self, entity_id: str) -> None:
        """Set the entity ID."""
        self._entity_id = entity_id

    @property
    def is_on(self) -> bool:
        """Return true if the device is charging."""
        # 首先尝试获取 charge 属性
        charge = self.traccar_position["attributes"].get("charge")
        if charge is not None:
            return charge
        
        # 如果没有 charge 属性，尝试其他可能的属性
        charging = self.traccar_position["attributes"].get("charging")
        if charging is not None:
            return charging
            
        # 如果都没有，尝试使用 ignition 属性（有些设备可能使用这个）
        return self.traccar_position["attributes"].get("ignition", False) 