"""Coordinate transformation utilities for ha_traccar."""
import math

# 地球半径
EARTH_RADIUS = 6378245.0
# 偏心率
EE = 0.00669342162296594323


def gcj02_to_wgs84(lng: float, lat: float) -> tuple[float, float]:
    """
    GCJ-02 坐标系 (火星坐标系) 转换为 WGS84 坐标系
    
    Args:
        lng: GCJ-02 坐标系的经度
        lat: GCJ-02 坐标系的纬度
        
    Returns:
        tuple: WGS84 坐标系的经度和纬度
    """
    if out_of_china(lng, lat):
        return lng, lat
    
    dlat = transform_lat(lng - 105.0, lat - 35.0)
    dlng = transform_lng(lng - 105.0, lat - 35.0)
    
    radlat = lat / 180.0 * math.pi
    magic = math.sin(radlat)
    magic = 1 - EE * magic * magic
    sqrtmagic = math.sqrt(magic)
    
    dlat = (dlat * 180.0) / ((EARTH_RADIUS * (1 - EE)) / (magic * sqrtmagic) * math.pi)
    dlng = (dlng * 180.0) / (EARTH_RADIUS / sqrtmagic * math.cos(radlat) * math.pi)
    
    mglat = lat + dlat
    mglng = lng + dlng
    
    return lng * 2 - mglng, lat * 2 - mglat


def transform_lat(lng: float, lat: float) -> float:
    """经纬度转换辅助函数"""
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + 0.1 * lng * lat + 0.2 * math.sqrt(abs(lng))
    ret += (20.0 * math.sin(6.0 * lng * math.pi) + 20.0 * math.sin(2.0 * lng * math.pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * math.pi) + 40.0 * math.sin(lat / 3.0 * math.pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * math.pi) + 320 * math.sin(lat * math.pi / 30.0)) * 2.0 / 3.0
    return ret


def transform_lng(lng: float, lat: float) -> float:
    """经纬度转换辅助函数"""
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + 0.1 * lng * lat + 0.1 * math.sqrt(abs(lng))
    ret += (20.0 * math.sin(6.0 * lng * math.pi) + 20.0 * math.sin(2.0 * lng * math.pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * math.pi) + 40.0 * math.sin(lng / 3.0 * math.pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * math.pi) + 300.0 * math.sin(lng / 30.0 * math.pi)) * 2.0 / 3.0
    return ret


def out_of_china(lng: float, lat: float) -> bool:
    """判断是否在中国境外"""
    if lng < 72.004 or lng > 137.8347:
        return True
    if lat < 0.8293 or lat > 55.8271:
        return True
    return False 