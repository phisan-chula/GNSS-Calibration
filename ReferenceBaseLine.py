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

class BaseLine:
    def __init__(self):
        self.g = Geod(ellps='WGS84')
        self.lat2,self.lon2 = [ 13.75, 100.50  ]  # fixed !
        self.Az12 = 45.000
        self.BL_hae = -32  # meter
        self.TABLE = list()

    def PrintBase(self):
        print( f'Reference : {self.g}' )
        print( f'Target P2 at : {self.lat2:.9f} {self.lon2:.9f}' )
        print( f'               {dms.toDMS(self.lat2,prec=5)}  {dms.toDMS(self.lon2,prec=5)} ' )
        print( f'Elevation P1/P2 HAE : {self.BL_hae:.3f} meter' )

    def Calc_BL(self, lat1, lon1 ):
        az12,az21,s12  = self.g.inv(lon1, lat1, self.lon2, self.lat2, radians=False )
        #import pdb;pdb.set_trace()
        XYZ1 = pm.geodetic2ecef( lat1,      lon1,      self.BL_hae , deg=True)
        XYZ2 = pm.geodetic2ecef( self.lat2, self.lon2, self.BL_hae, deg=True)
        bl = np.linalg.norm( np.array(XYZ2)-np.array(XYZ1) )
        self.TABLE.append( [  f'{lat1:.9f}' , dms.toDMS( lat1, prec=5),         
                              f'{lon1:.9f}' , dms.toDMS( lon1, prec=5),
                              f'{az12:.4f}' , dms.toDMS( az12, prec=0),
                              f'{s12:.3f}', 
                              f'{bl:.3f}', 
                           ] )
                           

    def Solve_Geodesic(self, S ):
        def ObjFunc(X0, lat2, lon2, az12, s12, g ):
            lat1,lon1 = X0
            az12_,_,s12_  = g.inv(lon1, lat1, lon2, lat2, radians=False )
            lon2_,lat2_,_ = g.fwd(lon1, lat1, az12, s12, radians=False)
            #import pdb;pdb.set_trace()
            L2norm =  np.linalg.norm( np.array( [lat2_-lat2,lon2_-lon2, s12_-s12, az12_-az12 ] ) )
            return L2norm
        lat1,lon1 = 13.00,100.00  # initial !!!
        res = fmin( ObjFunc, np.array([lat1,lon1]) , 
                    args=( self.lat2, self.lon2, self.Az12, S, self.g ), 
                    xtol=1E-12, ftol=1E-12, maxiter=1000, disp=True )
        print( res )
        #import pdb; pdb.set_trace()
        CHK = '''GeodSolve -i --input-string "{} {} {} {}"'''.format( 
                res[0], res[1], self.lat2, self.lon2 )
        print( CHK )
        os.system( CHK )
        return res # lat1, lon1

    def Solve_Baseline(self, BL ):
        def ObjFunc(X0, lat2, lon2, az12, bl,bl_hae, g ):
            lat1,lon1 = X0
            az12_,_,s12_  = g.inv(lon1, lat1, lon2, lat2, radians=False )
            lon2_,lat2_,_ = g.fwd(lon1, lat1, az12_, s12_, radians=False)
            #import pdb;pdb.set_trace()
            XYZ1 = pm.geodetic2ecef( lat1, lon1, bl_hae , deg=True)
            XYZ2 = pm.geodetic2ecef( lat2, lon2, bl_hae , deg=True)
            bl_ = np.linalg.norm( np.array(XYZ2)-np.array(XYZ1) )
            #print( f'>>>>>>>> {bl_:}' )
            L2norm =  np.linalg.norm( 
                          np.array( [lat2_-lat2, lon2_-lon2, bl_-bl, az12_-az12 ] ) )
            return L2norm
        lat1,lon1 = 13.00,100.00  # initial !!!
        res = fmin( ObjFunc, np.array([lat1,lon1]) , 
                    args=( self.lat2, self.lon2, self.Az12, BL, self.BL_hae, self.g ), 
                    xtol=1E-5, ftol=1E-5, maxiter=3000, disp=True )
        print( res )
        #import pdb; pdb.set_trace()
        CHK = '''GeodSolve -i --input-string "{} {} {} {}"'''.format( 
                res[0], res[1], self.lat2, self.lon2 )
        print( CHK )
        os.system( CHK )
        return res # lat1, lon1


##################################################
bl = BaseLine()
for S in [2,5,10,20,50]:
    print(f'=================== geodesic length = {S:} km  ==================')
    #lat1,lon1 = bl.Solve_Geodesic(  S =S*1_000  )
    lat1,lon1 = bl.Solve_Baseline(  BL=S*1_000  )  # a bit neater ....
    bl.Calc_BL( lat1, lon1 )

tab = pd.DataFrame( bl.TABLE, columns=[
       'P1_lat','P1_lat_','P1_lng','P1_lng_','az12', 'az12_','s12','baseline' ] )

bl.PrintBase()
import pdb; pdb.set_trace()
print(tab.to_markdown(floatfmt='.9f') ) 

