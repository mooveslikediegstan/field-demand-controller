# -*- coding: utf-8 -*-
import math

EARTH_RADIUS_KM = 6371.0
ROAD_CORRECTION_FACTOR = 1.35

def distance_between_coordinates(
    lat_origin: float, lon_origin: float,
    lat_dest: float, lon_dest: float,
    apply_correction: bool = True
    ) -> float:
    
    """
    Calcula distância entre dois pontos via Haversine.
    Equivalente ao DistanceBetweenCities() do VBA.
    """
    lat_o = math.radians(lat_origin)
    lon_o = math.radians(lon_origin)
    lat_d = math.radians(lat_dest)
    lon_d = math.radians(lon_dest)

    d_lat = lat_d - lat_o
    d_lon = lon_d - lon_o

    a = math.sin(d_lat / 2) ** 2 + math.cos(lat_o) * math.cos(lat_d) * math.sin(d_lon / 2) ** 2
    angle = math.asin(math.sqrt(a))

    factor = ROAD_CORRECTION_FACTOR if apply_correction else 1.0
    return 2 * EARTH_RADIUS_KM * factor * angle