"""Support for ha_traccar device tracking."""
from __future__ import annotations

import re
from typing import Any

from homeassistant.components.device_tracker import SourceType, TrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import Entity

from .const import (
    ATTR_ADDRESS,
    ATTR_ALTITUDE,
    ATTR_CATEGORY,
    ATTR_GEOFENCE,
    ATTR_MOTION,
    ATTR_SPEED,
    ATTR_STATUS,
    ATTR_TRACCAR_ID,
    ATTR_TRACKER,
    DOMAIN,
)
from .coord_transform import gcj02_to_wgs84
from .coordinator import TraccarServerCoordinator
from .entity import TraccarServerEntity, generate_entity_id


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up device tracker entities."""
    coordinator: TraccarServerCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = []
    for device_entry in coordinator.data.values():
        device = device_entry["device"]
        device_name = device["name"]
        # 处理设备名称，转换为有效的实体ID格式
        device_id = re.sub(r'[^\w\s]', '', device_name.lower()).replace(" ", "_")
        
        # 添加标准设备跟踪器
        tracker = TraccarServerDeviceTracker(coordinator, device)
        # 强制设置实体ID
        tracker.entity_id = f"device_tracker.{device_id}"
        entities.append(tracker)
        
        # 添加WGS84设备跟踪器
        wgs84_tracker = TraccarServerWGS84DeviceTracker(coordinator, device)
        # 强制设置实体ID
        wgs84_tracker.entity_id = f"device_tracker.{device_id}_wgs84"
        entities.append(wgs84_tracker)
    
    async_add_entities(entities)


class TraccarServerDeviceTracker(TraccarServerEntity, TrackerEntity):
    """Represent a tracked device."""

    def __init__(self, coordinator: TraccarServerCoordinator, device: dict) -> None:
        """Initialize the device tracker."""
        super().__init__(coordinator, device)
        # 使用设备名称作为实体名称
        self._attr_name = device["name"]
        # 设置与官方版本一致的unique_id
        self._attr_unique_id = self._device_id
        
    @property
    def entity_id(self) -> str:
        """Return the entity ID."""
        device_id = re.sub(r'[^\w\s]', '', self._device_name.lower()).replace(" ", "_")
        return f"device_tracker.{device_id}"
        
    @entity_id.setter
    def entity_id(self, entity_id: str) -> None:
        """Set the entity ID."""
        self._entity_id = entity_id

    @property
    def battery_level(self) -> int:
        """Return battery value of the device."""
        return self.traccar_position["attributes"].get("batteryLevel", -1)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return device specific attributes."""
        geofence_name = self.traccar_geofence["name"] if self.traccar_geofence else None
        return {
            **self.traccar_attributes,
            ATTR_ADDRESS: self.traccar_position["address"],
            ATTR_ALTITUDE: self.traccar_position["altitude"],
            ATTR_CATEGORY: self.traccar_device["category"],
            ATTR_GEOFENCE: geofence_name,
            ATTR_MOTION: self.traccar_position["attributes"].get("motion", False),
            ATTR_SPEED: self.traccar_position["speed"],
            ATTR_STATUS: self.traccar_device["status"],
            ATTR_TRACCAR_ID: self.traccar_device["id"],
            ATTR_TRACKER: DOMAIN,
        }

    @property
    def latitude(self) -> float:
        """Return latitude value of the device."""
        return self.traccar_position["latitude"]

    @property
    def longitude(self) -> float:
        """Return longitude value of the device."""
        return self.traccar_position["longitude"]

    @property
    def location_accuracy(self) -> int:
        """Return the gps accuracy of the device."""
        return self.traccar_position["accuracy"]

    @property
    def source_type(self) -> SourceType:
        """Return the source type, eg gps or router, of the device."""
        return SourceType.GPS


class TraccarServerWGS84DeviceTracker(TraccarServerEntity, TrackerEntity):
    """Represent a tracked device with WGS84 coordinates."""
    
    _attr_icon = "mdi:account-arrow-right"

    def __init__(self, coordinator: TraccarServerCoordinator, device: dict) -> None:
        """Initialize the device tracker."""
        super().__init__(coordinator, device)
        # 设置与官方版本一致的unique_id
        self._attr_unique_id = f"{self._device_id}_wgs84"
        # 使用设备名称 + WGS84 作为实体名称
        self._attr_name = f"{device['name']} WGS84"
        
    @property
    def entity_id(self) -> str:
        """Return the entity ID."""
        device_id = re.sub(r'[^\w\s]', '', self._device_name.lower()).replace(" ", "_")
        return f"device_tracker.{device_id}_wgs84"
        
    @entity_id.setter
    def entity_id(self, entity_id: str) -> None:
        """Set the entity ID."""
        self._entity_id = entity_id

    @property
    def battery_level(self) -> int:
        """Return battery value of the device."""
        return self.traccar_position["attributes"].get("batteryLevel", -1)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return device specific attributes."""
        geofence_name = self.traccar_geofence["name"] if self.traccar_geofence else None
        # 转换坐标
        lng, lat = gcj02_to_wgs84(
            self.traccar_position["longitude"],
            self.traccar_position["latitude"]
        )
        return {
            **self.traccar_attributes,
            ATTR_ADDRESS: self.traccar_position["address"],
            ATTR_ALTITUDE: self.traccar_position["altitude"],
            ATTR_CATEGORY: self.traccar_device["category"],
            ATTR_GEOFENCE: geofence_name,
            ATTR_MOTION: self.traccar_position["attributes"].get("motion", False),
            ATTR_SPEED: self.traccar_position["speed"],
            ATTR_STATUS: self.traccar_device["status"],
            ATTR_TRACCAR_ID: self.traccar_device["id"],
            ATTR_TRACKER: DOMAIN,
            "wgs84_longitude": lng,
            "wgs84_latitude": lat,
        }

    @property
    def latitude(self) -> float:
        """Return latitude value of the device in WGS84."""
        # 转换坐标
        _, lat = gcj02_to_wgs84(
            self.traccar_position["longitude"],
            self.traccar_position["latitude"]
        )
        return lat

    @property
    def longitude(self) -> float:
        """Return longitude value of the device in WGS84."""
        # 转换坐标
        lng, _ = gcj02_to_wgs84(
            self.traccar_position["longitude"],
            self.traccar_position["latitude"]
        )
        return lng

    @property
    def location_accuracy(self) -> int:
        """Return the gps accuracy of the device."""
        return self.traccar_position["accuracy"]

    @property
    def source_type(self) -> SourceType:
        """Return the source type, eg gps or router, of the device."""
        return SourceType.GPS
