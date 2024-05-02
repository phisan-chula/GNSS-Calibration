#
#
#
import os
import pymap3d as pm
import numpy as np
import pandas as pd
from scipy.optimize import fmin,minimize
from pyproj import Geod
from pygeodesy import dms

'''
WatSutat
  GeoidEval -n tgm2017-1 --msltohae --input-string "13.75 100.5 1.5"
  13.75 100.5 -29.0718
DoiIntanon
  GeoidEval -n tgm2017-1 --msltohae --input-string "18.60 98.50 2565"
  18.60 98.50 2526.7938
  GeoidEval -n tgm2017-1 --msltohae --input-string "18.60 98.50 300"
  18.60 98.50 261.7938
'''
class BaseLine:
    def __init__(self):
        self.g = Geod(ellps='WGS84')
        self.TABLE = list()
        if 1:  # WatSutat
            self.lat2, self.lon2 = [ 13.75, 100.50  ]  # fixed !
            self.Az12 = 45.000
            self.BL_hae = [-30,-32]  # meter
        else:  # Intanon  
            self.lat2, self.lon2 = [ 18.60, 98.50  ]  # fixed !
            self.Az12 = 225.000 
            self.BL_hae = [ 260 , 2526]  # meter

    def PrintBase(self):
        print( f'Reference : {self.g}' )
        print( f'Target P2 at : {self.lat2:.9f} {self.lon2:.9f}' )
        print( f'               {dms.toDMS(self.lat2,prec=5)}  {dms.toDMS(self.lon2,prec=5)} ' )
        print( f'Elevation P1/P2 hae : {self.BL_hae[0]:.3f} / {self.BL_hae[1]:.3f} meter' )

    def TableBL(self, lat1, lon1 ):
        az12,az21,s12  = self.g.inv(lon1, lat1, self.lon2, self.lat2, radians=False )
        az12 = divmod( az12,360 )[1]  # pyproj.Geod.fwd  return +/-180 !
        XYZ1 = pm.geodetic2ecef( lat1,      lon1,      self.BL_hae[0], deg=True)
        XYZ2 = pm.geodetic2ecef( self.lat2, self.lon2, self.BL_hae[1], deg=True)
        bl = np.linalg.norm( np.array(XYZ2)-np.array(XYZ1) )
        self.TABLE.append( [  f'{lat1:.9f}' , dms.toDMS( lat1, prec=5),         
                              f'{lon1:.9f}' , dms.toDMS( lon1, prec=5),
                              f'{az12:.4f}' , dms.toDMS( az12, prec=0),
                              f'{s12:.3f}', f'{bl:.3f}' ] )

    def Solve_Baseline(self, BL ):
        def ObjFunc(X0, lat2, lon2, az12, bl,bl_hae, g ):
            #import pdb; pdb.set_trace()
            lat1,lon1 = X0
            az12_,_,s12_  = g.inv(lon1, lat1, lon2, lat2, radians=False )
            az12_ = divmod( az12_,360 )[1]  # pyproj.Geod.fwd  return +/-180 !
            lon2_,lat2_,_ = g.fwd(lon1, lat1, az12_, s12_, radians=False)
            XYZ1 = pm.geodetic2ecef( lat1, lon1, bl_hae[0] , deg=True)
            XYZ2 = pm.geodetic2ecef( lat2, lon2, bl_hae[1] , deg=True)
            bl_ = np.linalg.norm( np.array(XYZ2)-np.array(XYZ1) )
            #print( f'>>>>>>>> {bl_:}' )
            L2norm =  np.linalg.norm( 
                          np.array( [lat2_-lat2, lon2_-lon2, bl_-bl, az12_-az12 ] ) )
            return L2norm
        az21 = divmod(self.Az12+180,360)[1]  # reverse az
        lon1_,lat1_,_ = self.g.fwd(self.lon2, self.lat2, az21, BL, radians=False)
        res = fmin( ObjFunc, np.array([lat1_,lon1_]) , 
                    args=( self.lat2, self.lon2, self.Az12, BL, self.BL_hae, self.g ), 
                    xtol=1E-4, ftol=1E-9, maxiter=1000, disp=True )
        print( res )
        CHK = '''GeodSolve -i --input-string "{} {} {} {}"'''.format( 
                                res[0], res[1], self.lat2, self.lon2 )
        print( CHK )
        os.system( CHK )
        return res # lat1, lon1

##################################################
ref = BaseLine()
for bl in [ 2, 5,10,20,50]:
    print(f'=================== baseline length = {bl:} km  ==================')
    lat1,lon1 = ref.Solve_Baseline( bl*1_000 )  # a bit neater ....
    ref.TableBL( lat1, lon1 )

tab = pd.DataFrame( ref.TABLE, columns=[
       'P1_lat','P1_lat_','P1_lng','P1_lng_','az12', 'az12_','s12','baseline' ] )

print('============ summary ==============')
ref.PrintBase()
FMT = (None,'.9f',None,'.9f',None,'.6f', None,'.3f', '.3f' )
print( tab.to_markdown( floatfmt=FMT  ) ) 
#import pdb; pdb.set_trace()

