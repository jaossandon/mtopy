import numpy as np

def geog_to_pol_wgs84_71S(lat, lon):
    """
    Transforms from geodetic coordinates (lat, lon) to Southern Hemisphere 
    polar stereographic coordinates (x, y) with latitude of true scale at 71S.
    
    Reference:
    Snyder, John P. Map Projections Used by the United States Geological Survey-2nd edition.
    U.S.G.S. Bulletin No. 1532. Washington D.C.: U.S. Government Printing Office, 1983.
    
    Parameters:
    lat (float or np.ndarray): Latitude in degrees.
    lon (float or np.ndarray): Longitude in degrees.
    
    Returns:
    tuple: x, y coordinates in polar stereographic projection.
    """
    
    # Conversion factor from degrees to radians
    dtorad = np.pi / 180.0

    # Latitude of true scale
    phi_c = -71
    lon0 = 0

    # WGS84 ellipsoid parameters
    a = 6378137.0
    f = 1 / 298.257223563
    e2 = 2 * f - f ** 2
    e = np.sqrt(e2)

    # Snyder equations 12-15 and 13-9 evaluated at latitude of true scale
    m_c = np.cos(phi_c * dtorad) / np.sqrt(1 - e2 * (np.sin(phi_c * dtorad)) ** 2)
    t_c = np.tan(np.pi / 4 + phi_c * dtorad / 2) / ((1 + e * np.sin(phi_c * dtorad)) / (1 - e * np.sin(phi_c * dtorad))) ** (e / 2)

    # Snyder equation 13-9 evaluated at specified latitudes
    t = np.tan(np.pi / 4 + lat * dtorad / 2) / ((1 + e * np.sin(lat * dtorad)) / (1 - e * np.sin(lat * dtorad))) ** (e / 2)

    # Snyder equation 17-34
    rho = a * m_c * t / t_c

    # Snyder equations 17-30 and 17-31
    x = -rho * np.sin((lon0 - lon) * dtorad)
    y = rho * np.cos((lon0 - lon) * dtorad)

    return x, y
