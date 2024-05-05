'''
GenRefBL.py : generates ia reference geodetic baseline 
between two points (P1 and P2) with a specified length (k kilometers) 
and forward azimuth (az21).

This straight-line baseline is an approximation of the true geodesic line, 
which is the shortest path between two points on an ellipsoid 
The script acknowledges that the generated straight-line baseline 
(chord) will have a small difference compared to the true geodesic line 
(s12) projected onto the ellipsoid surface.
'''

import os
import pymap3d as pm
import numpy as np
import pandas as pd
from scipy.optimize import fmin,minimize
from pyproj import Geod
from pygeodesy import dms

class BaseLine:
    def __init__(self):
        self.g = Geod(ellps='WGS84')
        self.TABLE  = list()
        self.TABLE_ = list()
        if 1:  # WatSutat
            self.lat2, self.lon2 = [ 13.75, 100.50  ]  # fixed !
            self.az2 = 45.000
            self.BL_hae = [ -32 , -30]  # meter
        else:  # Intanon  
            self.lat2, self.lon2 = [ 18.60, 98.50  ]  # fixed !
            self.az2 = -135.000   #-180 < az <+180 
            self.BL_hae = [ 260 , 2526]  # meter  !!! DeltaH >> S12
        assert -90  <=self.lat2 <=+90
        assert -180 <=self.lon2 <=+180
        assert -180 <=self.az2  <=+180

    def PJ4_Inverse( self, lat1, lon1, lat2, lon2 ):
        ''' return forward azimuth at starting and terminus, -180 < az <+180 '''
        fwd_az1, bwd_az2, s12  = self.g.inv(lon1, lat1, lon2, lat2, radians=False )
        return fwd_az1,AzTrunc180(bwd_az2+180),s12

    def PJ4_Direct( self, lat1, lon1, az1, s12 ):
        ''' return lon2,lat2 of the terminus, also fwd_az2 at the terminus'''
        ''' PJ4_fwd() gives back azimuths of terminus!!!, reverse to forward'''
        lon2,lat2,bwd_az2  = self.g.fwd(lon1, lat1, az1, s12, radians=False )
        return lat2,lon2,AzTrunc180( bwd_az2+180 )

    def PrintBaseLine(self):
        print( f'Reference : {self.g}' )
        print( f'Target to P2:  phi lam  faz' )
        print( f'{self.lat2:.9f} {self.lon2:.9f}, {self.az2:.9f} ' )
        print( f'{dms.toDMS(self.lat2,prec=5)}  {dms.toDMS(self.lon2,prec=5)} '\
               f'{dms.toDMS(self.az2,prec=5)}' )
        print( f'Elevation P1/P2 hae : {self.BL_hae[0]:.3f} / {self.BL_hae[1]:.3f} meter' )
        COLS = [ 'baseline','s12', 
                 'P1_lat','P1_lng','P1_hae','P2_lat','P2_lng','P2_hae', 'faz1', 'faz2' ] 
        self.dfTABLE = pd.DataFrame( self.TABLE, columns=COLS )
        self.dfTABLE_ = pd.DataFrame( self.TABLE_, columns=COLS )
        #import pdb; pdb.set_trace()
        FMT = (None, '.3f','.3f','.9f','.9f','.3f','.9f','.9f','.3f', '.7f', '.7f')
        print( self.dfTABLE.to_markdown( floatfmt=FMT ) )
        print()
        FMT_ = (None, '.3f','.3f',None,None,'.3f',None,None,'.3f',None,None)
        print( self.dfTABLE_.to_markdown( floatfmt=FMT_  ) )
        self.dfTABLE_.to_pickle( "./TableBaseline.pkl" )

    def TableBL(self, lat1, lon1 ):
        az1, az2, s12 = self.PJ4_Inverse( lat1,lon1, self.lat2, self.lon2 )
        XYZ1 = pm.geodetic2ecef( lat1,      lon1,      self.BL_hae[0], deg=True)
        XYZ2 = pm.geodetic2ecef( self.lat2, self.lon2, self.BL_hae[1], deg=True)
        bl = np.linalg.norm( np.array(XYZ2)-np.array(XYZ1) )
        self.TABLE.append( [ f'{bl:.3f}' , f'{s12:.3f}',
                 f'{lat1:.9f}',     f'{lon1:.9f}',     f'{self.BL_hae[0]:.3f}',
                 f'{self.lat2:.9f}',f'{self.lon2:.9f}',f'{self.BL_hae[1]:.3f}',
                 f'{az1:.9f}',f'{az2:.9f}'   ] )
        self.TABLE_.append( [ f'{bl:.3f}' , f'{s12:.3f}',
          f'{dms.toDMS(lat1,prec=5)}', f'{dms.toDMS(lon1,prec=5)}', f'{self.BL_hae[0]:.3f}',
          f'{dms.toDMS(self.lat2,prec=5)}',f'{dms.toDMS(self.lon2,prec=5)}',f'{self.BL_hae[1]:.3f}',
          f'{dms.toDMS(az1,prec=2)}',f'{dms.toDMS(az2,prec=2)}'   ] )

    def Solve_Baseline(self, BL ):
        """ solve for baseline of length 'BL' , give terminus point lat2,lon2
            and its forward azimuth 'fwd_az2. Height above ellipsoid 'hae' of
            both ends are constrainted.
            returns:
                lat1,lon1 of the starting
        """
        def ObjFunc(X0, lat2, lon2, fwd_az2, BL, hae, g ):
            #print( X0, lat2, lon2, fwd_az2, BL, hae, g )
            lat1,lon1 = X0
            fwd_az1_,fwd_az2_,s12_  = self.PJ4_Inverse(lat1,lon1,lat2,lon2 )
            XYZ1 = pm.geodetic2ecef( lat1, lon1, hae[0] , deg=True)
            XYZ2 = pm.geodetic2ecef( lat2, lon2, hae[1] , deg=True)
            bl_ = np.linalg.norm( np.array(XYZ2)-np.array(XYZ1) )
            #import pdb; pdb.set_trace()
            diff_az2 = AzTrunc180( fwd_az2_-fwd_az2 )
            L2norm = np.linalg.norm( np.array([bl_-BL ,diff_az2] ) )
            return L2norm
        lat1_,lon1_,_ = self.PJ4_Direct(self.lat2, self.lon2, AzTrunc180(180+self.az2), BL)
        res = fmin( ObjFunc, np.array([lat1_,lon1_]) , 
                    args=( self.lat2, self.lon2, self.az2, BL, self.BL_hae, self.g ), 
                    xtol=1E-4, ftol=1E-9, maxiter=1000, disp=True )
        print( res )
        CHK = '''GeodSolve -i --input-string "{} {} {} {}"'''.format( 
                                res[0], res[1], self.lat2, self.lon2 )
        print( CHK )
        os.system( CHK )
        return res # lat1, lon1

def AzTrunc180( az ):
    ''' truncating azimuth [-180...+180] degree '''
    _, az360 = divmod(az, 360) # round-off to one-circle
    div,mod = divmod( az360, 180 )
    if div>=1: return mod-180
    else: return mod

##################################################
ref = BaseLine()
for bl in [ 2, 5,10,20,50]:
    print(f'=================== baseline length = {bl:} km  ==================')
    lat1,lon1 = ref.Solve_Baseline( bl*1_000 )  # a bit neater ....
    ref.TableBL( lat1, lon1 )

print('========================== summary ============================')
ref.PrintBaseLine()
#import pdb; pdb.set_trace()

