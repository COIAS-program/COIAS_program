#!/usr/bin/env python3
# -*- coding: UTF-8 -*
# Time-stamp: <2022/04/13 12:00:00 (JST) KS>

import numpy as np
from astroquery.jplhorizons import Horizons
import time
import re
from astropy.io import fits
import glob
import traceback
import requests.exceptions

#--function----------------------------------------------------------------------------
# get info from jpl horizons
def getinfo(x):
    # print(name_list[x])
    radec =[]
    # tentative prevention of error (2022.4.8 KS)################################
    try:
        objRadec = Horizons(id=name_list[x],location='568',epochs=time_list2[0:5],id_type="smallbody").ephemerides()['targetname','datetime_jd','RA','DEC','V']
    except ValueError:
        print("We cannot get information of id="+name_list[x]+" from JPL.")
        global NLoseAsteroids
        NLoseAsteroids += 1
    else:
        for i in range(Ndata):
            if isCorrectDirectory[i]==0:
                radec.append(objRadec[i])
    ############################################################################
        
    return radec
#---------------------------------------------------------------------------------------

try:
    #---main--------------------------------------------------------------------------------
    t1 = time.time()
    # if have_all_precise_orbits.txt has 1, then known objects in all warp files were already searched,
    # so we skip all process in this script
    haveAllPreciseOrbitsFile = open("have_all_precise_orbits.txt","r")
    haveAllPreciseOrbits = int(haveAllPreciseOrbitsFile.readline().rstrip("\n"))
    haveAllPreciseOrbitsFile.close()

    if(haveAllPreciseOrbits==0):
        #---read precise_orbit_directories.txt---------------------------------------
        Ndata = 5
        NShouldGetPreciseOrbit = 0
        directoryNames = []
        isCorrectDirectory = []
        preciseOrbitDirectoriesFile = open("precise_orbit_directories.txt","r")
        for i in range(Ndata):
            content = preciseOrbitDirectoriesFile.readline().split()
            directoryNames.append(content[0])
            isCorrectDirectory.append(int(content[1]))
            if isCorrectDirectory[i]==0:
                NShouldGetPreciseOrbit += 1
        preciseOrbitDirectoriesFile.close()
        #----------------------------------------------------------------------------
    
        # read scidata
        img_list = sorted(glob.glob('warp[1-5]_bin.fits'))
        if len(img_list)==0:
            raise FileNotFoundError
    
        time_list = []
        for i in range(len(img_list)):
            scidata = fits.open( img_list[i] )
            jd = scidata[0].header['JD']
            time_list.append( jd )
        
        # time_list
        time_list2 = [np.round(float(time_list[i]),decimals=8) for i in range(len(time_list))]  
        
        # numbered name_list
        tmp2 = str("cand3.txt")
        tmp4 = open(tmp2,"r")
        name1 = tmp4.readlines()
        name_list =[]
        for i in name1:
            name_list.append(i.rstrip('\n'))
        # time
        # time1 = time_list[0]
            
        # number of name
        nn = len(name_list)
            
        ## number of asteroids we cannot get information from JPL (2022.4.8 KS)########
        NLoseAsteroids = 0
        ###############################################################################

        #if __name__ == "__main__":
        #    with Pool(10) as p:
        #        print(p.map(getinfo,range(nn)))
        #        print(p.map(f,range(nn)))
        #        tmp10 = p.map(getinfo,range(nn))
    
        ## tentative treatment (2022.4.8 KS)############################################
        # tmp10 = list(map(getinfo,range(nn)))
            
        tmp10 = []
        for i in range(nn):
            recvRadec = getinfo(i)
            if len(recvRadec)!=0:
                tmp10.append(recvRadec)
                    
        nn = nn - NLoseAsteroids
        tmp5 = np.array(tmp10)
        tmp5.reshape(nn,1,NShouldGetPreciseOrbit)
                    
        # tmp5 = np.array(tmp10)
        ################################################################################
                    
        # K.S. modifies 2022/4/13###########################
        temporary = np.ndarray((nn, NShouldGetPreciseOrbit, 5),dtype=object)
        for i1 in range(nn):
            for i2 in range (NShouldGetPreciseOrbit):
                for i3 in range(5):
                    temporary[i1, i2, i3] = tmp5[i1][i2][i3]
                                    
        tmp6 = temporary.reshape(nn*NShouldGetPreciseOrbit,5)
        ####################################################
        # tmp7 =[]
        tmp7 = np.empty(0)
                                    
        for i in range(len(img_list)):
            for k in range(len(tmp6)):
                #        print(tmp6[k,1],time_list2[i],i,k)
                if tmp6[k,1] - 0.0000001 <time_list2[i] and tmp6[k,1] +0.000001 > time_list2[i]:
                    #                   print(tmp6[k],file_list[i])
                    tmp7 = np.append(tmp7,tmp6[k])
                    #tmp7 = np.append(tmp7,file_list[i])
                    tmp7 = np.append(tmp7, str(i)) # NM 2021.07.08
        tmp8 = tmp7.reshape(int(len(tmp7)/6),6)
                                                
        # remove name and karifugo from numberd
        for l in range(len(tmp8)):
            tmp9 = re.sub(r"\(.+?\)","",tmp8[l,0]) # remove karifugo
            tmp11 = re.sub(r"[a-zA-Z\']","",tmp9) # remove name
            tmp12 = tmp11.rstrip()
            tmp8[l,0] = tmp12
        
        fList = np.ndarray((5),dtype=object)
        for i in range(Ndata):
            if isCorrectDirectory[i]==0:
                fList[i] = open(directoryNames[i]+"/numbered_new2B.txt","w",newline="\n")

        for i in range(len(tmp8)):
            fList[int(tmp8[i,5])].write(tmp8[i,0]+" "+str(tmp8[i,1])+" "+str(tmp8[i,2])+" "+str(tmp8[i,3])+" "+str(tmp8[i,4])+"\n")

        for i in range(Ndata):
            if isCorrectDirectory[i]==0:
                fList[i].close()
        
        t2 = time.time()    
        elapsed_time = t2 -t1
        print("getinfo numbered, Elapsed time:", elapsed_time)

except requests.exceptions.ConnectionError:
    print("You do not connect to the internet in getinfo_numbered2D.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 32

except requests.exceptions.ConnectTimeout:
    print("Connection timeout to NASA JPL in getinfo_numbered2D.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 33

except FileNotFoundError:
    print("Some previous files are not found in getinfo_numbered2D.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 34

except Exception:
    print("Some errors occur in getinfo_numbered2D.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 35

else:
    error = 0
    errorReason = 34

finally:
    errorFile = open("error.txt","a")
    errorFile.write("{0:d} {1:d} 314 \n".format(error,errorReason))
    errorFile.close()
