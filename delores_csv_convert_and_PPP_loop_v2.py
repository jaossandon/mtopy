import os
import helper_functions as hf
import pandas as pd

def main():
    # Set main folder
    main_folder = r'C:\Users\Felipe Napoleoni\Documents\MATLAB\Delores\GHOST'
    subdirs = [d for d in os.listdir(main_folder) if os.path.isdir(os.path.join(main_folder, d)) and d not in ['.', '..']]
    
    for subdir in subdirs:
        subdir_path = os.path.join(main_folder, subdir)
        print(f'Processing directory: {subdir_path}')
        
        events_file = os.path.join(subdir_path, 'EVENTS.CSV')
        positions_file = os.path.join(subdir_path, 'positions_polar.dat')
        
        if os.path.exists(positions_file):
            print(f'Found positions_polar.dat in {subdir}. Skipping...')
            continue
        
        if os.path.exists(events_file):
            print(f'Running full conversion on {subdir_path}')
            out = hf.optdelcsvread3()
            
            gps_positions, gps_time_date = hf.CanadianGPStoDELCSV_ECK_onePPP(subdir_path, 'dGPS2_combined_data.csv', hf.LEAP_SECONDS)
            out['GPSPositions'] = gps_positions
            out['GPSTimeDate'] = gps_time_date
            
            out = hf.travdis2(out)
            
            write_output_files(subdir_path, subdir, out)
        else:
            print(f'No useful files found in {subdir}: Skipping this directory.')

def write_output_files(subdir_path, subdir, out):
    os.chdir(subdir_path)
    
    # Write positions CSV
    positions_df = pd.DataFrame({
        'Latitude': out['ShotPositions']['Lats'],
        'Longitude': out['ShotPositions']['Longs'],
        'Elevation': out['ShotPositions']['Elevation'],
        'ShotNumber': np.arange(1, len(out['ShotPositions']['Lats']) + 1)
    })
    positions_df.to_csv(f'{subdir}_positions.csv', index=False)
    
    # Write positions polar DAT
    x, y = hf.geog_to_pol_wgs84_71S(out['ShotPositions']['Lats'], out['ShotPositions']['Longs'])
    positions_polar_df = pd.DataFrame({
        'X': x,
        'Y': y,
        'Elevation': out['ShotPositions']['Elevation'],
        'ShotNumber': np.arange(1, len(x) + 1)
    })
    positions_polar_df.to_csv(f'{subdir}_positions_polar.dat', index=False, header=False)
    
    # Write reflex positions DST
    reflex_positions_df = pd.DataFrame({
        'ShotNumber': np.arange(1, len(x) + 1),
        'Distance': np.zeros(len(x)),
        'X': x,
        'Y': y,
        'X2': x,
        'Y2': y,
        'Elevation1': out['ShotPositions']['Elevation'],
        'Elevation2': out['ShotPositions']['Elevation']
    })
    reflex_positions_df.to_csv(f'{subdir}_reflexpositions.dst', index=False, header=False, sep=' ')

if __name__ == "__main__":
    main()
