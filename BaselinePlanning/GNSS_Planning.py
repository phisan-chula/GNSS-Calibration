#
#
#  GNSS Baseline planning
#
#
import pandas as pd
import geopandas as gpd
from sklearn.cluster import DBSCAN
import numpy as np
import shapely
import toml
from shapely.geometry import LineString,Point,box
gpd.options.io_engine = "pyogrio"

class Network:
    def __init__( self, TOML ):
        with open( TOML,'r') as f:
            self.TOML = toml.load( f)
        self.ReadPnt( self.TOML['point_kml'] )
        df = gpd.read_file( 'CORS_NCDC_2024.gpkg' )
        BOX = box(*self.PNTS.total_bounds).buffer( 100/111)   # km
        #import pdb ;pdb.set_trace()
        self.dfCORS = df[ df.geometry.intersects( BOX ) ]
        self.AllPNT = pd.concat( [self.dfCORS[['STA','geometry']],
                       self.PNTS[['STA','geometry']] ] )

    def ReadPnt(self,KML ):
        ''' read points from [network] , make station name "P-1,P-2,P-3" etc. '''
        df = gpd.read_file(KML , driver='KML')
        df = df[['Name','geometry']].copy()
        df['Pnt'] = df.index+1
        def MakePnt(row):
            pnt = Point(  row.geometry.x, row.geometry.y )
            return [f'P-{row.Pnt}', row.geometry.x, row.geometry.y,pnt]
        df[ ['STA','x','y','geometry']] = df.apply( MakePnt, axis=1, result_type='expand' )
        XY = df[['x','y']].to_numpy()
        clustering = DBSCAN(eps=200/111_000 , min_samples=2).fit(XY)
        print( clustering.labels_ )
        self.PNTS = gpd.GeoDataFrame( df , crs='EPSG:4326', geometry=df.geometry )

    def CreateBaseLine( self ):
        ''' create baseline from string of point , estimate kilometer and duration
            in minute for GNSS baseline observation '''
        dfs = list()
        for line,pnts in self.TOML['network'].items():
            LIN = list()
            for i in range( len(pnts)-1 ): 
                fr = self.AllPNT[self.AllPNT.STA==pnts[i] ].iloc[0].geometry
                to = self.AllPNT[self.AllPNT.STA==pnts[i+1] ].iloc[0].geometry
                LS = LineString( [ fr, to ] )
                LIN.append( [ line,pnts[i],pnts[i+1],LS ] )
            dfs.append( pd.DataFrame( LIN,columns=['Loop','FR','TO','geometry'] ) )
        dfBL = pd.concat( dfs,ignore_index=True  )
        self.gdfBL = gpd.GeoDataFrame( dfBL, crs='EPSG:4326', geometry=dfBL.geometry )
        def CalcBL(row):
            km = 111*row.geometry.length
            if km<=5 : mins=20   # Tech.spec.NSW 2ndControl 2021
            else: mins=int(2*km+10)
            km = f'{km:.1f} km'
            return km,mins
        self.gdfBL[['km','mins']] = self.gdfBL.apply( CalcBL, axis=1, result_type='expand' )
        pnts = pd.DataFrame( nw.gdfBL[['FR','TO']].values.flatten() )
        cors = pnts[~pnts[0].str.startswith('P-') ]
        cors = self.dfCORS[ self.dfCORS.STA.isin( cors[0].tolist() ) ]
        self.CORS = cors[['STA','X','Y','Z','Lat','Long','h','epoch']]
        # GeoidEval -n "egm2008-1" --haetomsl --input-string "14 100 -56"

    def _CORS_exists(self, BL_SESS ):
        ''' check if ['P-1', 'CORS' ]  in CORS ? '''
        return self.CORS['STA'].isin( BL_SESS ).any()

    def _CORS_remove(self, STA_SESS ):
        ''' remove CORS form list e.g. remove 'AWLK' from
             [P-27, P-25, AWLK, P-12] and return [P-27, P-25, P-12] '''
        assert len( self.CORS[ self.CORS['STA'].isin( STA_SESS )] ) == 1
        CORS = self.CORS[ self.CORS['STA'].isin( STA_SESS )].iloc[0].STA
        STA = pd.Series( STA_SESS )
        return STA[STA != CORS ]

    def BLSession_Occupation( self ):
        ''' generate indepent baseline Rovers + CORS '''
        GNSS_RCV = self.TOML['receiver']
        INDEP_BL = len( GNSS_RCV )-1
        SESS = list()
        for loop,baseline in self.gdfBL.groupby( 'Loop' ):
            #print( f'=============={trav}===============' )
            FULL,REST = divmod( len(baseline),INDEP_BL)
            STA = pd.Series( baseline[['FR','TO']].values.flatten() ).unique()
            ibl = 0
            while ibl<len(baseline):
                fr = ibl
                to = fr + INDEP_BL    # last index could over-run!
                rcv_bl = baseline.iloc[fr:to] 
                rcv_sta = pd.Series( rcv_bl[['FR','TO']].values.flatten() ).unique()
                if self._CORS_exists( rcv_sta ):
                    fr = ibl
                    to = fr + INDEP_BL + 1    # last index could over-run!
                    sess_bl  = baseline.iloc[fr:to] 
                    baselines = pd.Series( sess_bl[['FR','TO']].values.flatten() ).unique()
                    sta_occu = self._CORS_remove( baselines )
                else:
                    baselines = rcv_sta
                    sta_occu = rcv_sta
                #print( rcv_bl )
                SESS.append(  [ loop, rcv_bl['mins'].max(), sta_occu.tolist(), baselines.tolist() ]  )  
                ibl = to
        self.SESS = pd.DataFrame( SESS, columns=['Loop', 'duration', 'sta_occu', 'baselines' ] )
        #import pdb ; pdb.set_trace()

    def BLSessionCLK( self):
        DAY = 1
        CLK_BEG = pd.Timestamp( self.TOML['begin'] ) 
        clk = list()
        for loop_name, loop in self.SESS.groupby( 'Loop' ):
            #print( f'=============={loop}===============' )
            for i, row in loop.iterrows(): 
                DURAT = row['duration']
                CLK_END = CLK_BEG + pd.Timedelta( minutes=DURAT)
                clk.append( [ DAY, CLK_BEG.strftime('%H:%M'), CLK_END.strftime('%H:%M') ] )
                CLK_BEG = CLK_BEG + pd.Timedelta( minutes=DURAT) +\
                                     pd.Timedelta( minutes=self.TOML['travel'] )
                if CLK_END>=pd.Timestamp(self.TOML['end']):
                    CLK_BEG = pd.Timestamp( self.TOML['begin'] )
                    DAY = DAY+1
        self.SESS[['day','clk_beg','clk_end']] = clk
        self.SESS = self.SESS[['Loop',  'day', 'duration', 'clk_beg', 'clk_end', 
                               'sta_occu',  'baselines' ]] 
        #import pdb ; pdb.set_trace()

    def GenLocation(self):
        locs = list()
        for i,row in self.SESS.iterrows():
            LOC = list()
            for i in row.sta_occu:
                name = self.PNTS[self.PNTS.STA==i].iloc[0].Name
                LOC.append( name )
            locs.append( LOC )
        self.SESS['locations'] = locs
        #import pdb ; pdb.set_trace()

    def PlotGPKG(self):
        GPKG = "./CACHE/RockArt_Baseline.gpkg"
        print(f'Plotting baseline {GPKG} ...' )
        for loop,gdf in self.gdfBL.groupby('Loop'):
            #import pdb ; pdb.set_trace()
            gdf.to_file(GPKG, layer=f'L:{loop}', driver="GPKG")
        self.dfCORS.to_file(GPKG, layer='CORS', driver="GPKG")
        self.PNTS.to_file(GPKG, layer='Station', driver="GPKG")

####################################################################33
#####################################################################33
#####################################################################33
TOML = 'PangnaArt.toml'
nw = Network( TOML )
print( f'Project:   {nw.TOML["project"]}' )
print( f'PointKML:  {nw.TOML["point_kml"]}' )
print( f'Receivers:  {nw.TOML["receiver"]}' )
print( f'Work Hour:  {nw.TOML["begin"]} to {nw.TOML["end"]}' )
print( f'Transport time:  {nw.TOML["travel"]} minutes' )
nw.CreateBaseLine()
nw.PlotGPKG()
nw.BLSession_Occupation()
nw.BLSessionCLK( )
nw.GenLocation()
nw.SESS.rename( columns={ 'sta_occu':  str(nw.TOML['receiver']) }, inplace=True )
print( '=== GNSS Occupation Session ===' )
COLS = nw.SESS.columns
print( nw.SESS[COLS[:-1]].to_markdown()  )
import pdb ;pdb.set_trace()
if 0:
    FMT =(None,None,'15.3f','15.3f','15.3f','^20s' ) 
    print( nw.SESS[COLS[-4:]].to_markdown()  )
    print( nw.CORS[['STA', 'X','Y','Z','epoch']].to_markdown( floatfmt=FMT ) )
