#!/usr/bin/env python3
# -*- coding: UTF-8 -*
#timestamp: 2022/6/26 17:30 sugiura

import glob
import os
import traceback
import re

try:
    #---open output file and write header-----------------------
    outputFile = open("final_all.txt","w",newline="\n")
    originalImgNames = sorted(glob.glob('warp-*.fits'))
    for i in range(len(originalImgNames)):
        outputFile.write("{:d}: ".format(i)+originalImgNames[i]+"\n")
    #-----------------------------------------------------------

    #---get number of new objects and name range----------------
    HNList = []
    HNMax=0
    HNMin=1000000000 #VERY LARGE VALUE
    preRepoFile = open("pre_repo2.txt","r")
    preRepoLines = preRepoFile.readlines()
    preRepoFile.close()
    for line in preRepoLines:
        thisName = line.split()[0]
        if re.search(r'^H......', thisName)!=None:
            thisHN = int(thisName.lstrip("H"))
            if thisHN not in HNList:
                HNList.append(thisHN)
            if thisHN > HNMax: HNMax = thisHN
            if thisHN < HNMin: HNMin = thisHN

    outputFile.write("The number of new objects: {0:d} \n".format(len(HNList)))
    outputFile.write("Range of new object names: H" + str(HNMin).rjust(6,"0") + " - H" + str(HNMax).rjust(6,"0") + "\n")
    #-----------------------------------------------------------

    #---get H conversion list-----------------------------------
    HConversionListFile = open("H_conversion_list_automanual3.txt","r")
    lines = HConversionListFile.readlines()
    HOld = []
    HNew = []
    for l in range(len(lines)):
        lineList = lines[l].split()
        HOld.append(lineList[2])
        HNew.append(lineList[3])
    HConversionListFile.close()
    #-----------------------------------------------------------

    #---search newall_automanual2.txt to produce final all------
    #---we also produce final_disp.txt from pre_repo2.txt-------
    fileFinalDisp = open("final_disp.txt","w",newline="\n")
    
    fileNewAllAutomanual = open("newall_automanual2.txt","r")
    newAllLines = fileNewAllAutomanual.readlines()
    fileNewAllAutomanual.close()
    for l in range(len(preRepoLines)):
        thisName = preRepoLines[l].split()[0]
        ## search this old name
        if re.search(r'^H......', thisName)==None:
            thisOldName = thisName
        else:
            for l2 in range(len(HNew)):
                if thisName==HNew[l2]:
                    thisOldName = HOld[l2]

        ## search the same line in newall_automanual2.txt
        for newAllOneLine in newAllLines:
            if preRepoLines[l].replace(thisName, thisOldName)[0:31] == newAllOneLine[0:31]:
                contents = newAllOneLine.split()
                fileFinalDisp.write(thisName + " " + contents[13] + " " + contents[16] + " " + contents[17] + "\n")
                outputFile.write(newAllOneLine.replace(thisOldName, thisName))

        ## output contents of orbital_element_summary_web.txt###
        if (l==len(preRepoLines)-1 or len(preRepoLines[l+1].split())==0 or preRepoLines[l+1].split()[0]!=thisName) and os.path.isfile("orbital_elements_summary_web.txt"):
            if len(thisName)==7:
                headSpace="     "
            elif len(thisName)==5:
                headSpace=""
            
            orbElemFile = open("orbital_elements_summary_web.txt","r")
            orbElemLines = orbElemFile.readlines()
            orbElemFile.close()

            for l2 in range(len(orbElemLines)):
                if orbElemLines[l2].split()[0].rstrip(":")==thisOldName:
                    outputFile.write(headSpace + orbElemLines[l2].replace(thisOldName, thisName))
                    outputFile.write(headSpace + orbElemLines[l2+1])
                    outputFile.write(headSpace + orbElemLines[l2+2])
                    outputFile.write("\n")
                    break

    fileFinalDisp.close()
    outputFile.close()
    #-----------------------------------------------------------
    

except FileNotFoundError:
    print("Some previous files are not found in make_final_all.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 74

except Exception:
    print("Some errors occur in make_final_all.py!")
    print(traceback.format_exc())
    error = 1
    errorReason = 75

else:
    error = 0
    errorReason = 74

finally:
    errorFile = open("error.txt","a")
    errorFile.write("{0:d} {1:d} 707 \n".format(error,errorReason))
    errorFile.close()
