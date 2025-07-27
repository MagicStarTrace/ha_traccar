"""Base entity for ha_traccar."""
from __future__ import annotations

import re
from typing import Any

from pytraccar import DeviceModel, GeofenceModel, PositionModel

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, ENTITY_ID_MAP
from .coordinator import TraccarServerCoordinator


def generate_entity_id(device_name: str, suffix: str) -> str:
    """Generate an entity ID using device name and English suffixes."""
    # 处理设备名称，转换为有效的实体ID格式
    device_id = re.sub(r'[^\w\s]', '', device_name.lower()).replace(" ", "_")
    
    # 转换后缀为英文（如果有映射）
    if suffix in ENTITY_ID_MAP:
        suffix = ENTITY_ID_MAP[suffix]
    
    return f"{device_id}_{suffix}"


class TraccarServerEntity(CoordinatorEntity[TraccarServerCoordinator]):
    """Base entity for ha_traccar."""

    _attr_has_entity_name = False

    def __init__(
        self,
        coordinator: TraccarServerCoordinator,
        device: DeviceModel,
    ) -> None:
        """Initialize the ha_traccar entity."""
        super().__init__(coordinator)
        self.device_id = device["id"]
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device["uniqueId"])},
            model=device["model"],
            name=device["name"],
        )
        # 保存设备ID和名称
        self._device_id = device["uniqueId"]
        self._device_name = device["name"]
        
        # 设置默认的entity_id前缀，使用设备名称
        self.entity_id_prefix = re.sub(r'[^\w\s]', '', device["name"].lower()).replace(" ", "_")

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return bool(self.coordinator.data and self.device_id in self.coordinator.data)

    @property
    def traccar_device(self) -> DeviceModel:
        """Return the device."""
        return self.coordinator.data[self.device_id]["device"]

    @property
    def traccar_geofence(self) -> GeofenceModel | None:
        """Return the geofence."""
        return self.coordinator.data[self.device_id]["geofence"]

    @property
    def traccar_position(self) -> PositionModel:
        """Return the position."""
        return self.coordinator.data[self.device_id]["position"]

    @property
    def traccar_attributes(self) -> dict[str, Any]:
        """Return the attributes."""
        return self.coordinator.data[self.device_id]["attributes"]

    async def async_added_to_hass(self) -> None:
        """Entity added to hass."""
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                f"{DOMAIN}_{self.device_id}",
                self.async_write_ha_state,
            )
        )
        await super().async_added_to_hass()
