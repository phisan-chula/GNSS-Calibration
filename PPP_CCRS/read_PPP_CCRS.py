import PyPDF2
import pandas as pd
import geopandas as gpd
import pymap3d as p3d
from pathlib import Path
import numpy as np
from pygeodesy.dms import toDMS, parseDMS
import cartopy.crs as ccrs
import matplotlib.pyplot as plt


def dt( str_dt ):
    return pd.to_datetime( str_dt )
def flt( str_m ):
    return float(str_m.split()[0])

def GetResultPPP( PDF ):
    pdf_file = open( PDF , 'rb')
    pdf_reader = PyPDF2.PdfReader(pdf_file)

    text = ''
    for page_num in range(len(pdf_reader.pages)):
      page = pdf_reader.pages[page_num]
      text += page.extract_text()

    df = pd.DataFrame( {"text":text.splitlines()} )
    df.text=df.text.str.strip()

    SRC_TXT = "Estimated Position for "
    search = df[df['text'].str.contains( SRC_TXT )]
    IDX = search.index[0]

    RINEX = search.iloc[0].text[len(SRC_TXT): ]
    data = {
        'RINEX'     : RINEX,
        'POINT'     : RINEX.split('_')[0],
        'RefFrame'  : df.iloc[41].text,
        'ObsBeg'    : dt(df.iloc[7].text),  'ObsEnd' : dt(df.iloc[8].text), 'Dura'  : df.iloc[9].text,
        'Lat'       : df.iloc[42].text,   'Lng'    : df.iloc[43].text, 'Hae'     : df.iloc[44].text,
        'StdLat' : flt( df.iloc[46].text ),  'StdLng' : flt( df.iloc[46].text ), 'StdHae' : flt( df.iloc[46].text ),
    }
    data_ = { 'Lat_': parseDMS( data['Lat'] ) , 'Lng_': parseDMS( data['Lng']), 'Hae_': flt( data['Hae'] ) }
    #import pdb ; pdb.set_trace()
    return data|data_

def CalcVelocity( dfPPP ):
    diff = list()
    for grp,df in dfPPP.groupby('POINT'):
        fr = df.iloc[0]
        to = df.iloc[1]
        assert len(df)==2
        assert fr.POINT == to.POINT
        fr_ = fr.ObsBeg + (fr.ObsEnd-fr.ObsBeg)/2
        to_ = to.ObsBeg + (to.ObsEnd-to.ObsBeg)/2
        lat_ = (fr.Lat_+to.Lat_)/2
        lng_ = (fr.Lng_+to.Lng_)/2
        days = (to_-fr_).days
        enu = p3d.geodetic2enu( to.Lat_,to.Lng_,to.Hae_, fr.Lat_, fr.Lng_, fr.Hae_, deg=True )
        enu_mm = 1000*np.array( enu )
        enu_mma = 1000*(np.array( enu )/days)*365.25  #  vde,vdn,ddh  ....mm/a
        #print( df )
        print( 'Pnt: {:5}   dE: {:5.1f} mm.  dN: {:5.1f} mm.     dh: {:5.1f} mm.'.format( grp, *enu_mm ) )
        diff.append( [grp, to_.date(), days, *enu_mm, *enu_mma, lat_,lng_] )

    dfVFLD = pd.DataFrame( diff, columns=[
        'Pnt', 'till_date', 'days', 'dE_mm', 'dN_mm', 'dh_mm', 'vE_mma', 'vN_mma', 'vh_mma', 'lat', 'lng' ] )
    gdfVFLD = gpd.GeoDataFrame( dfVFLD, crs='EPSG:4326',
                        geometry=gpd.points_from_xy( dfVFLD.lng, dfVFLD.lat ) )
    #import pdb ; pdb.set_trace()
    return gdfVFLD

def PlotVelociy( dfVELO, TITLE, VERT=False ):
    if VERT: AXIS = 'Vert'; ANG=90
    else:    AXIS = 'Hori'; ANG=0
    extent = [93, 112, 2, 25]
    fig = plt.figure( figsize=(15, 10 ) )
    PROJ = ccrs.PlateCarree()
    ax = plt.axes(projection=PROJ )
    ax.stock_img()
    ax.coastlines()
    ax.set_extent( extent, crs=PROJ )
    for Pnt,df in dfVELO.iterrows():
        ax.text( df.lng, df.lat, df.Pnt, transform=PROJ, color='r' )
        if VERT:
            q = ax.quiver( df.lng, df.lat, 0.0, df.vh_mma, scale=200, color='r' ) 
        else:
            q = ax.quiver( df.lng, df.lat, df.vE_mma, df.vN_mma, scale=200, color='r' ) 
    ax.plot( dfVELO.lng, dfVELO.lat, "r.", ms=5, transform=PROJ ) 
    qk = plt.quiverkey( q, 0.8, 0.2, 30, f'{AXIS} velocity (30 mm/a)', 
                           angle=ANG,  labelpos='S', transform=PROJ, color='r')
    #plt.show()
    print(f'Plotting stress {TITLE} ....') 
    plt.title(TITLE)
    plt.savefig(f'CACHE/Stress{AXIS}Velocity.pdf')
    plt.savefig(f'CACHE/Stress{AXIS}Velocity.png')

    
##################################################################
#PDF = 'GNSS_StressModelling/NTSK_20240325-080553.pdf'
ppp = list()
for pdf in Path('./GNSS_StressModelling/').glob('*.pdf'):
    data = GetResultPPP( pdf )
    ppp.append(data)
dfPPP = pd.DataFrame( ppp )
dfPPP.sort_values( by=['POINT','ObsBeg'] , inplace=True )
print( dfPPP) 

print( dfPPP[['StdLat', 'StdLng', 'StdHae' ]].describe() )

dfvelo = CalcVelocity( dfPPP )
print( dfvelo )

velo_till = str( dfvelo.till_date.min() + (dfvelo.till_date.max() - dfvelo.till_date.min())/2 )
velo_days = '{:.1f} days'.format( dfvelo.days.mean() )

PlotVelociy( dfvelo, TITLE=f'Horizontal Stress Velocity on {velo_till} from PPP/GNSS {velo_days}', VERT=False )
PlotVelociy( dfvelo, TITLE=f'Vertical Stress Velocity on {velo_till} from PPP/GNSS {velo_days}', VERT=True )
######################################################

import pdb ; pdb.set_trace()
