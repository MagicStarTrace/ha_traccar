"""Support for ha_traccar sensors."""
from __future__ import annotations

import re
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfLength,
    UnitOfSpeed,
    UnitOfTemperature,
)
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
    """Set up sensor entities."""
    coordinator: TraccarServerCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = []
    for device_entry in coordinator.data.values():
        device = device_entry["device"]
        device_name = device["name"]
        # 处理设备名称，转换为有效的实体ID格式
        device_id = re.sub(r'[^\w\s]', '', device_name.lower()).replace(" ", "_")
        
        # 创建电池传感器
        battery_sensor = TraccarServerBatterySensor(coordinator, device)
        battery_sensor.entity_id = f"sensor.{device_id}_battery"
        entities.append(battery_sensor)
        
        # 创建海拔传感器
        altitude_sensor = TraccarServerAltitudeSensor(coordinator, device)
        altitude_sensor.entity_id = f"sensor.{device_id}_altitude"
        entities.append(altitude_sensor)
        
        # 创建速度传感器
        speed_sensor = TraccarServerSpeedSensor(coordinator, device)
        speed_sensor.entity_id = f"sensor.{device_id}_speed"
        entities.append(speed_sensor)
        
        # 创建方向传感器
        course_sensor = TraccarServerCourseSensor(coordinator, device)
        course_sensor.entity_id = f"sensor.{device_id}_course"
        entities.append(course_sensor)
        
        # 创建地址传感器
        address_sensor = TraccarServerAddressSensor(coordinator, device)
        address_sensor.entity_id = f"sensor.{device_id}_address"
        entities.append(address_sensor)
        
        # 创建地理围栏传感器
        geofence_sensor = TraccarServerGeofenceSensor(coordinator, device)
        geofence_sensor.entity_id = f"sensor.{device_id}_geofence"
        entities.append(geofence_sensor)
        
        # 创建温度传感器（如果有）
        if "deviceTemp" in device_entry["position"]["attributes"]:
            temp_sensor = TraccarServerTemperatureSensor(coordinator, device)
            temp_sensor.entity_id = f"sensor.{device_id}_temperature"
            entities.append(temp_sensor)
        
        # 创建距离传感器（如果有）
        if "totalDistance" in device_entry["position"]["attributes"]:
            distance_sensor = TraccarServerDistanceSensor(coordinator, device)
            distance_sensor.entity_id = f"sensor.{device_id}_distance"
            entities.append(distance_sensor)
    
    async_add_entities(entities)


class TraccarServerBatterySensor(TraccarServerEntity, SensorEntity):
    """Represent a battery sensor."""

    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_icon = "mdi:battery"

    def __init__(self, coordinator: TraccarServerCoordinator, device: dict) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, device)
        self._attr_unique_id = f"{self._device_id}_battery"
        self._attr_name = f"{device['name']} 电池"
    
    @property
    def entity_id(self) -> str:
        """Return the entity ID."""
        device_id = re.sub(r'[^\w\s]', '', self._device_name.lower()).replace(" ", "_")
        return f"sensor.{device_id}_battery"
        
    @entity_id.setter
    def entity_id(self, entity_id: str) -> None:
        """Set the entity ID."""
        self._entity_id = entity_id

    @property
    def native_value(self) -> int:
        """Return the value of the sensor."""
        battery_level = self.traccar_position["attributes"].get("batteryLevel", 0)
        # 如果已经是百分比值（0-100），直接返回
        if battery_level > 1:
            return round(battery_level)
        # 如果是小数（0-1），转换为百分比
        return round(battery_level * 100)


class TraccarServerAltitudeSensor(TraccarServerEntity, SensorEntity):
    """Represent an altitude sensor."""

    _attr_device_class = SensorDeviceClass.DISTANCE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfLength.METERS
    _attr_icon = "mdi:altimeter"

    def __init__(self, coordinator: TraccarServerCoordinator, device: dict) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, device)
        self._attr_unique_id = f"{self._device_id}_altitude"
        self._attr_name = f"{device['name']} 海拔"
    
    @property
    def entity_id(self) -> str:
        """Return the entity ID."""
        device_id = re.sub(r'[^\w\s]', '', self._device_name.lower()).replace(" ", "_")
        return f"sensor.{device_id}_altitude"
        
    @entity_id.setter
    def entity_id(self, entity_id: str) -> None:
        """Set the entity ID."""
        self._entity_id = entity_id

    @property
    def native_value(self) -> int:
        """Return the value of the sensor."""
        return round(self.traccar_position["altitude"])


class TraccarServerSpeedSensor(TraccarServerEntity, SensorEntity):
    """Represent a speed sensor."""

    _attr_device_class = SensorDeviceClass.SPEED
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfSpeed.KILOMETERS_PER_HOUR
    _attr_icon = "mdi:speedometer"

    def __init__(self, coordinator: TraccarServerCoordinator, device: dict) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, device)
        self._attr_unique_id = f"{self._device_id}_speed"
        self._attr_name = f"{device['name']} 速度"
    
    @property
    def entity_id(self) -> str:
        """Return the entity ID."""
        device_id = re.sub(r'[^\w\s]', '', self._device_name.lower()).replace(" ", "_")
        return f"sensor.{device_id}_speed"
        
    @entity_id.setter
    def entity_id(self, entity_id: str) -> None:
        """Set the entity ID."""
        self._entity_id = entity_id

    @property
    def native_value(self) -> float:
        """Return the value of the sensor."""
        return self.traccar_position["speed"] * 3.6


class TraccarServerCourseSensor(TraccarServerEntity, SensorEntity):
    """Represent a course sensor."""

    _attr_icon = "mdi:compass"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "°"

    def __init__(self, coordinator: TraccarServerCoordinator, device: dict) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, device)
        self._attr_unique_id = f"{self._device_id}_course"
        self._attr_name = f"{device['name']} 方向"
    
    @property
    def entity_id(self) -> str:
        """Return the entity ID."""
        device_id = re.sub(r'[^\w\s]', '', self._device_name.lower()).replace(" ", "_")
        return f"sensor.{device_id}_course"
        
    @entity_id.setter
    def entity_id(self, entity_id: str) -> None:
        """Set the entity ID."""
        self._entity_id = entity_id

    @property
    def native_value(self) -> float:
        """Return the value of the sensor."""
        return self.traccar_position["course"]


class TraccarServerTemperatureSensor(TraccarServerEntity, SensorEntity):
    """Represent a temperature sensor."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    def __init__(self, coordinator: TraccarServerCoordinator, device: dict) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, device)
        self._attr_unique_id = f"{self._device_id}_temperature"
        self._attr_name = f"{device['name']} 温度"
    
    @property
    def entity_id(self) -> str:
        """Return the entity ID."""
        device_id = re.sub(r'[^\w\s]', '', self._device_name.lower()).replace(" ", "_")
        return f"sensor.{device_id}_temperature"
        
    @entity_id.setter
    def entity_id(self, entity_id: str) -> None:
        """Set the entity ID."""
        self._entity_id = entity_id

    @property
    def native_value(self) -> float:
        """Return the value of the sensor."""
        return self.traccar_position["attributes"].get("deviceTemp", 0)


class TraccarServerDistanceSensor(TraccarServerEntity, SensorEntity):
    """Represent a distance sensor."""

    _attr_device_class = SensorDeviceClass.DISTANCE
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfLength.KILOMETERS
    _attr_icon = "mdi:map-marker-distance"

    def __init__(self, coordinator: TraccarServerCoordinator, device: dict) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, device)
        self._attr_unique_id = f"{self._device_id}_distance"
        self._attr_name = f"{device['name']} 距离"
    
    @property
    def entity_id(self) -> str:
        """Return the entity ID."""
        device_id = re.sub(r'[^\w\s]', '', self._device_name.lower()).replace(" ", "_")
        return f"sensor.{device_id}_distance"
        
    @entity_id.setter
    def entity_id(self, entity_id: str) -> None:
        """Set the entity ID."""
        self._entity_id = entity_id

    @property
    def native_value(self) -> int:
        """Return the value of the sensor."""
        # 将米转换为千米并取整数
        distance_meters = self.traccar_position["attributes"].get("totalDistance", 0)
        return round(distance_meters / 1000)


class TraccarServerAddressSensor(TraccarServerEntity, SensorEntity):
    """Represent an address sensor."""

    _attr_icon = "mdi:map-marker-outline"

    def __init__(self, coordinator: TraccarServerCoordinator, device: dict) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, device)
        self._attr_unique_id = f"{self._device_id}_address"
        self._attr_name = f"{device['name']} 地址"
    
    @property
    def entity_id(self) -> str:
        """Return the entity ID."""
        device_id = re.sub(r'[^\w\s]', '', self._device_name.lower()).replace(" ", "_")
        return f"sensor.{device_id}_address"
        
    @entity_id.setter
    def entity_id(self, entity_id: str) -> None:
        """Set the entity ID."""
        self._entity_id = entity_id

    @property
    def native_value(self) -> str:
        """Return the value of the sensor."""
        return self.traccar_position["address"]


class TraccarServerGeofenceSensor(TraccarServerEntity, SensorEntity):
    """Represent a geofence sensor."""

    _attr_icon = "mdi:map-marker-radius"

    def __init__(self, coordinator: TraccarServerCoordinator, device: dict) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, device)
        self._attr_unique_id = f"{self._device_id}_geofence"
        self._attr_name = f"{device['name']} 地理围栏"
    
    @property
    def entity_id(self) -> str:
        """Return the entity ID."""
        device_id = re.sub(r'[^\w\s]', '', self._device_name.lower()).replace(" ", "_")
        return f"sensor.{device_id}_geofence"
        
    @entity_id.setter
    def entity_id(self, entity_id: str) -> None:
        """Set the entity ID."""
        self._entity_id = entity_id

    @property
    def native_value(self) -> str:
        """Return the value of the sensor."""
        if self.traccar_geofence:
            return self.traccar_geofence["name"]
        return "未知" 