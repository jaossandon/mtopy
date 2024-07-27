import sys
import os
import numpy as np
import pandas as pd
from pathlib import Path


# ______________________Select what to process_____________________
# Directly set the options for processing both channels

def outputs_needed(inputfiletype):
    CHA = True
    CHB = False
    return (CHA, CHB, 0, 0)


# ______________________Choose File________________
# Replace file selection dialog with a hardcoded file path

def File_Loc():
    filename = "C:/Users/Felipe Napoleoni/Desktop/dGPS/2023/1226/D1B03L01_WEST/EVENTS.CSV"
    return filename


# ___________________Input File Choice_______________________
# Directly set the input file type

def input_file():
    inputfiletype = ".CSV"
    return (inputfiletype)

# Transforms from geodetic coordinates (lat,lon) to Southern Hemisphere polar stereographic coordinates (x,y)
# with latitude of true scale at 71S.
# Transforms from geodetic coordinates (lat,lon) to
# Southern Hemisphere polar stereographic coordinates (x,y)
# with latitude of true scale at 71S.
# Reference:
# Snyder, John P. Map Projections Used by the United States Geological Survey-2nd edition.
# U.S.G.S. Bulletin No. 1532. Washington D.C.: U.S. Government Printing Office, 1983.

def geog_to_pol_wgs84_71S(lat, lon):
    pi = 3.141592653589793
    dtorad = pi / 180
    phi_c = -71
    lon0 = 0
    a = 6378137
    f = 1 / 298.257223563
    e2 = 2 * f - f ** 2
    e = np.sqrt(e2)
    m_c = np.cos(phi_c * dtorad) / np.sqrt(1 - e2 * (np.sin(phi_c * dtorad)) ** 2)
    t_c = np.tan(pi / 4 + phi_c * dtorad / 2) / ((1 + e * np.sin(phi_c * dtorad)) / (1 - e * np.sin(phi_c * dtorad))) ** (e / 2)
    t = (np.tan(pi / 4 + lat * dtorad / 2)) / ((1 + e * np.sin(lat * dtorad)) / (1 - e * np.sin(lat * dtorad))) ** (e / 2)
    rho = a * m_c * t / t_c
    x = -rho * (np.sin((lon0 - lon) * dtorad))
    y = rho * (np.cos((lon0 - lon) * dtorad))
    return [x, y]


# _________________Main Program______________
def optdelcsvread3():
    inputfiletype = input_file()
    filename = File_Loc()
    if filename is None:
        sys.exit()
    if inputfiletype == ".CSV":
        CSVFile = open(filename, "r")

    root = Path(filename).resolve().parent.name
    pathname = Path(filename).resolve().parent
    fileoutA = os.path.join(pathname, (root + '_CHA' + '.asm'))
    fileoutB = os.path.join(pathname, (root + '_CHB' + '.asm'))
    fileoutTIMEA = os.path.join(pathname, (root + '_TIMESA' + '.csv'))
    fileoutTIMEB = os.path.join(pathname, (root + '_TIMESB' + '.csv'))
    fileoutGPSA = os.path.join(pathname, (root + '_GPSA' + '.csv'))
    fileoutGPSB = os.path.join(pathname, (root + '_GPSB' + '.csv'))
    fileoutCSV = os.path.join(pathname, (root + '_META' + '.csv'))
    fileoutREFLEX = os.path.join(pathname, (root + '_REFLEX' + '.dst'))
    fileoutREFLEXPPP = os.path.join(pathname, (root + '_REFLEXPPP' + '.dst'))
    fileoutGIS = os.path.join(pathname, (root + '_GIS' + '.csv'))

    ChANeed, ChBNeed, CHASampleLength, CHBSampleLength = outputs_needed(inputfiletype)


# __________________ChA File________________
    if ChANeed:
        with open(fileoutA, 'a') as f, open(fileoutTIMEA, 'a') as ft, open(fileoutGPSA, 'a') as fg, open(fileoutREFLEX, 'a') as fr:
            count = 0
            if inputfiletype == ".CSV":
                CSVFile.seek(0)
                TraceNumber = 1
                SHOTline_number = 0
                CSVfile_line_number = 1
                GPSposition = ''
                Space_string = " "
                LastLineWasSHOT = False #True or False (False is default)
                ft.write('TraceNumber,CSVlineNumber,SysDate,SysTime,GPSLatDeg,GPSLatMin,GPSLonDeg,GPSLonMin,GPSelev\n')
                fg.write('CSVlineNumber,TraceNumber,SysDate,SysTime,GPSDate,GPSTime,GPSLatDeg,GPSLatMin,GPSLonDeg,GPSLonMin,GPSelev\n')
                for line in CSVFile:
                    CSV_line = line
                    if CSV_line[24:27] == 'GPS':
                        if LastLineWasSHOT:
                            SysDate = CSV_line[:10]
                            SysTime = CSV_line[11:23]
                            GPSDate = CSV_line[28:34]
                            GPStime = CSV_line[35:41]
                            GPSLatDeg = CSV_line[42:44]
                            GPSLatMin = CSV_line[44:51]
                            GPSLonDeg = CSV_line[54:57]
                            GPSLonMin = CSV_line[57:64]
                            GPSelev = CSV_line[67:72]
                            GPSlinenumber = str(CSVfile_line_number)
                            GPSposition = '-' + GPSLatDeg + ',' + GPSLatMin + ',' + '-' + GPSLonDeg + ',' + GPSLonMin + ',' + GPSelev
                            outputline = (GPSlinenumber + ',' + str(TraceNumber) + ',' + SysDate + ',' + SysTime + ',' + GPSDate + ',' + GPStime + ',' + GPSposition + '\n')
                            lat = -1 * (abs(float(GPSLatDeg)) + (float(GPSLatMin) / 60))
                            lon = -1 * (abs(float(GPSLonDeg)) + (float(GPSLonMin) / 60))
                            [x, y] = geog_to_pol_wgs84_71S(lat, lon)
                            x = round(x, 2)
                            y = round(y, 2)
                            fr.write(str(TraceNumber) + '    ' + '0' + ' ' + str(x) + ' ' + str(y) + ' ' + str(x) + ' ' + str(y) + '     ' + GPSelev + '     ' + GPSelev + '\n')
                            fg.write(outputline)
                            LastLineWasSHOT = False

                    if CSV_line[24:28] == "SHOT":
                        SHOTline_number = CSVfile_line_number
                        ShotDate = CSV_line[:10]
                        ShotTime = CSV_line[11:23]
                        Samp_No = int(CSV_line[33:38])
                        out_line = (CSV_line[39:].split("\t"))[:Samp_No]
                        final_output = " ".join(out_line)
                        f.write(final_output + '\n')
                        ft.write(str(TraceNumber) + ',' + str(SHOTline_number) + ',')
                        ft.write(ShotDate + ',' + ShotTime)
                        if not LastLineWasSHOT:
                            ft.write(',' + GPSposition + '\n')
                        else:
                            ft.write('\n')
                        TraceNumber = TraceNumber + 1
                        LastLineWasSHOT = True

                    CSVfile_line_number = CSVfile_line_number + 1

        print('completed A')


# __________________ChB File________________
    if ChBNeed:
        with open(fileoutB, 'a') as f, open(fileoutTIMEB, 'a') as ft, open(fileoutGPSB, 'a') as fg:
            if not ChANeed:
                with open(fileoutREFLEX, 'a') as fr:
                    count = 0
                    if inputfiletype == ".CSV":
                        CSVFile.seek(0)
                        TraceNumber = 1
                        SHOTline_number = 0
                        CSVfile_line_number = 1
                        GPSposition = ''
                        Space_string = " "
                        LastLineWasSHOT = False
                        ft.write('TraceNumber,CSVlineNumber,SysDate,SysTime,GPSLatDeg,GPSLatMin,GPSLonDeg,GPSLonMin,GPSelev\n')
                        fg.write('CSVlineNumber,TraceNumber,SysDate,SysTime,GPSDate,GPSTime,GPSLatDeg,GPSLatMin,GPSLonDeg,GPSLonMin,GPSelev\n')
                        for line in CSVFile:
                            CSV_line = line
                            if CSV_line[24:27] == 'GPS':
                                if LastLineWasSHOT:
                                    SysDate = CSV_line[:10]
                                    SysTime = CSV_line[11:23]
                                    GPSDate = CSV_line[28:34]
                                    GPStime = CSV_line[35:41]
                                    GPSLatDeg = CSV_line[42:44]
                                    GPSLatMin = CSV_line[44:51]
                                    GPSLonDeg = CSV_line[54:57]
                                    GPSLonMin = CSV_line[57:64]
                                    GPSelev = CSV_line[67:72]
                                    GPSlinenumber = str(CSVfile_line_number)
                                    GPSposition = '-' + GPSLatDeg + ',' + GPSLatMin + ',' + '-' + GPSLonDeg + ',' + GPSLonMin + ',' + GPSelev
                                    outputline = (GPSlinenumber + ',' + str(TraceNumber) + ',' + SysDate + ',' + SysTime + ',' + GPSDate + ',' + GPStime + ',' + GPSposition + '\n')
                                    if not ChANeed:
                                        lat = -1 * (abs(float(GPSLatDeg)) + (float(GPSLatMin) / 60))
                                        lon = -1 * (abs(float(GPSLonDeg)) + (float(GPSLonMin) / 60))
                                        [x, y] = geog_to_pol_wgs84_71S(lat, lon)
                                        x = round(x, 2)
                                        y = round(y, 2)
                                        fr.write(str(TraceNumber) + '    ' + '0' + ' ' + str(x) + ' ' + str(y) + ' ' + str(x) + ' ' + str(y) + '     ' + GPSelev + '     ' + GPSelev + '\n')
                                    fg.write(outputline)
                                    LastLineWasSHOT = False

                            if CSV_line[24:28] == "SHOT":
                                SHOTline_number = CSVfile_line_number
                                ShotDate = CSV_line[:10]
                                ShotTime = CSV_line[11:23]
                                Samp_No = int(CSV_line[33:38])
                                out_line = (CSV_line[39:].split("\t"))[Samp_No + 2:]
                                final_output = " ".join(out_line)
                                f.write(final_output)
                                ft.write(str(TraceNumber) + ',' + str(SHOTline_number) + ',')
                                ft.write(ShotDate + ',' + ShotTime)
                                if not LastLineWasSHOT:
                                    ft.write(',' + GPSposition + '\n')
                                else:
                                    ft.write('\n')
                                TraceNumber = TraceNumber + 1
                                LastLineWasSHOT = True

                            CSVfile_line_number = CSVfile_line_number + 1

        print('completed B')

print('Ready fredy!')