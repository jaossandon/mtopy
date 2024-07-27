import numpy as np
import pandas as pd
from scipy.signal import medfilt
from geopy.distance import geodesic

def m_lldist2(longitudes, latitudes):
    distances = [0]  # First distance is 0
    for i in range(1, len(longitudes)):
        dist = geodesic((latitudes[i-1], longitudes[i-1]), (latitudes[i], longitudes[i])).meters
        distances.append(dist)
    return np.array(distances)

def datenumvec(time_data):
    dates = pd.to_datetime({
        'year': time_data['Year'],
        'month': time_data['Month'],
        'day': time_data['Day'],
        'hour': time_data['Hour'],
        'minute': time_data['Minute'],
        'second': time_data['Second']
    })
    datenums = dates.map(lambda dt: dt.toordinal() + dt.hour / 24.0 + dt.minute / 1440.0 + dt.second / 86400.0)
    keep = np.arange(len(datenums))
    throw = np.array([])  # placeholder for any removal logic
    return datenums, keep, throw

def geog_to_pol_wgs84_71S(lat, lon):
    # Dummy conversion, should be replaced with actual logic for polar stereographic conversion
    return lat * 1000, lon * 1000

def travdis2(out):
    if isinstance(out, dict):  # Assuming out is a dict-like structure
        resanobj = False
    else:
        out = out.__dict__
        resanobj = True

    Lats = np.double(out['GPSPositions']['LatDegrees']) + \
           np.sign(out['GPSPositions']['LatDegrees']) * np.double(out['GPSPositions']['LatMinutes'] / 60)

    Longs = np.double(out['GPSPositions']['LongDegrees']) + \
            np.sign(out['GPSPositions']['LongDegrees']) * np.double(out['GPSPositions']['LongMinutes'] / 60)

    LatStart = np.ones(len(Lats)) * Lats[0]
    LongStart = np.ones(len(Longs)) * Longs[0]

    out['GPSPositions']['Distance'] = m_lldist2(Longs, Lats)
    out['GPSPositions']['NSDist'] = m_lldist2(Longs, LatStart) * np.sign(Longs - Longs[0])
    out['GPSPositions']['EWDist'] = m_lldist2(LongStart, Lats) * np.sign(Lats - Lats[0])

    GPSdNSDist = m_lldist2(Longs, LatStart)
    GPSdEWDist = m_lldist2(LongStart, Lats)
    out['GPSPositions']['DistanceTravelled'] = np.insert(np.cumsum(np.sqrt(GPSdNSDist**2 + GPSdEWDist**2)), 0, 0)

    out['GPSTimeDate']['Datenum'], keep, throw = datenumvec(out['GPSTimeDate'])

    for key in ['DistanceTravelled', 'Distance', 'NSDist', 'EWDist']:
        out['GPSPositions'][key] = np.array(out['GPSPositions'][key])[keep]

    Lats = Lats[keep]
    Longs = Longs[keep]
    out['GPSPositions']['Elevation'] = np.array(out['GPSPositions']['Elevation'])[keep]

    if 'ShotTimeDate' in out:
        out['ShotTimeDate']['Datenum'] = datenumvec(out['ShotTimeDate'])[0]
        
        if max(out['ShotTimeDate']['Datenum']) < min(out['GPSTimeDate']['Datenum']) or \
           min(out['ShotTimeDate']['Datenum']) > max(out['GPSTimeDate']['Datenum']):
            return out
        
        for key in ['DistanceTravelled', 'Distance', 'NSDist', 'EWDist']:
            out['ShotPositions'][key] = np.interp(out['ShotTimeDate']['Datenum'], out['GPSTimeDate']['Datenum'], out['GPSPositions'][key])

        out['ShotPositions']['Lats'] = np.interp(out['ShotTimeDate']['Datenum'], out['GPSTimeDate']['Datenum'], Lats)
        out['ShotPositions']['Longs'] = np.interp(out['ShotTimeDate']['Datenum'], out['GPSTimeDate']['Datenum'], Longs)
        out['ShotPositions']['Elevation'] = medfilt(np.interp(out['ShotTimeDate']['Datenum'], out['GPSTimeDate']['Datenum'], out['GPSPositions']['Elevation']), 9)

        nShots = len(out['ShotPositions']['Lats'])
        for i in range(1, nShots):
            if abs(out['ShotPositions']['Lats'][i] - out['ShotPositions']['Lats'][i - 1]) > 0.1:
                out['ShotPositions']['Lats'][i] = out['ShotPositions']['Lats'][i - 1]
            if abs(out['ShotPositions']['Longs'][i] - out['ShotPositions']['Longs'][i - 1]) > 0.1:
                out['ShotPositions']['Longs'][i] = out['ShotPositions']['Longs'][i - 1]

        pathstr, name = os.path.split(os.getcwd())
        
        positions_file = f"{name}_positions.csv"
        with open(positions_file, 'w') as fid:
            for i in range(nShots):
                fid.write(f"{out['ShotPositions']['Lats'][i]:.8f},{out['ShotPositions']['Longs'][i]:.8f},{out['ShotPositions']['Elevation'][i]:.2f},{i + 1}\r\n")

        positions_polar_file = f"{name}_positions_polar.dat"
        with open(positions_polar_file, 'w') as fid2:
            for i in range(nShots):
                x, y = geog_to_pol_wgs84_71S(out['ShotPositions']['Lats'][i], out['ShotPositions']['Longs'][i])
                fid2.write(f"{x:.2f},{y:.2f},{out['ShotPositions']['Elevation'][i]:.2f},{i + 1}\n")

        reflexpositions_file = f"{name}_reflexpositions.dst"
        with open(reflexpositions_file, 'w') as fid3:
            x_coords = []
            y_coords = []
            for i in range(nShots):
                x, y = geog_to_pol_wgs84_71S(out['ShotPositions']['Lats'][i], out['ShotPositions']['Longs'][i])
                x_coords.append(x)
                y_coords.append(y)
                reflexpositions = [i + 1, 0, x, y, x, y, out['ShotPositions']['Elevation'][i], out['ShotPositions']['Elevation'][i]]
                fid3.write(' '.join(map(str, reflexpositions)) + '\n')

    if resanobj:
        out = resan(out)

    return out
