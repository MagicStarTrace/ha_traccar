"""Constants for the ha_traccar integration."""
from logging import getLogger

DOMAIN = "ha_traccar"
LOGGER = getLogger(__package__)

ATTR_ADDRESS = "address"
ATTR_ALTITUDE = "altitude"
ATTR_CATEGORY = "category"
ATTR_GEOFENCE = "geofence"
ATTR_MOTION = "motion"
ATTR_SPEED = "speed"
ATTR_STATUS = "status"
ATTR_TRACKER = "tracker"
ATTR_TRACCAR_ID = "traccar_id"

CONF_MAX_ACCURACY = "max_accuracy"
CONF_CUSTOM_ATTRIBUTES = "custom_attributes"
CONF_EVENTS = "events"
CONF_SKIP_ACCURACY_FILTER_FOR = "skip_accuracy_filter_for"

# 中文名称到英文ID的映射
ENTITY_ID_MAP = {
    "运动": "motion",
    "状态": "status",
    "在线": "status",
    "充电": "charging",
    "地理围栏": "geofence",
    "地址": "address",
    "电池": "battery",
    "高度": "altitude",
    "海拔": "altitude",
    "速度": "speed",
    "方向": "course",
    "温度": "temperature",
    "距离": "distance",
}

EVENTS = {
    "deviceMoving": "device_moving",
    "commandResult": "command_result",
    "deviceFuelDrop": "device_fuel_drop",
    "geofenceEnter": "geofence_enter",
    "deviceOffline": "device_offline",
    "driverChanged": "driver_changed",
    "geofenceExit": "geofence_exit",
    "deviceOverspeed": "device_overspeed",
    "deviceOnline": "device_online",
    "deviceStopped": "device_stopped",
    "maintenance": "maintenance",
    "alarm": "alarm",
    "textMessage": "text_message",
    "deviceUnknown": "device_unknown",
    "ignitionOff": "ignition_off",
    "ignitionOn": "ignition_on",
}
