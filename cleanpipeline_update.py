#!/usr/bin/env python
"""
Meridith Joyce
Pipeline project
Objective: raw data goes in, reduced data comes out!
(1) remember to run ur_forget, ur_setup before executing
(2) this can be executed straight from the command line; directory finagling is automatic now
"""

from pyraf import iraf
from iraf import imarith, imcopy, hselect, imcombine 
from iraf import imstatistics as imstat
import glob
import os 
from iraf import noao, imred, bias, linebias

debug=False

catch=str(raw_input("copy files from a81images? (y) "))
if catch =="y":
	file_list=glob.glob("../a81images/*.fit")
	for f in file_list:
		pieces=f.split(".")	
		newname="f"+str(pieces[3]) + "." + str(pieces[4])	
		imcopy(f, newname)


mybias="[2050:2100,*]" 
mytrim = "[20:2000,*]" 
linebias("*.fit","*.fit",bias=mybias, trim = mytrim, function = "legendre", order = 1, low_reject = 3, high_reject = 3)


print "bias subtracted from all images!"

mylist_FF=hselect("f*","$I",'imagetyp=="FLATFIELD"',Stdout=1) #all flats
mylist_Obj= hselect("f*","$I",'imagetyp=="OBJECT"',Stdout=1) #all objects

I_band=hselect("f*","$I",'FILTPOS==5',Stdout=1) #filtpos 5 corresponds to I
V_band=hselect("f*","$I",'FILTPOS==7',Stdout=1) # V
B_band=hselect("f*","$I",'FILTPOS==3',Stdout=1) # B
Ikp=hselect("f*","$I",'FILTPOS==6',Stdout=1) # I-kp

megadict={
	"FF_B": [val for val in mylist_FF if val in B_band],
	"FF_I": [val for val in mylist_FF if val in I_band],
	"FF_V": [val for val in mylist_FF if val in V_band],
	"FF_Ikp": [val for val in mylist_FF if val in Ikp],
	"obj_B": [val for val in mylist_Obj if val in B_band], 
	"obj_I": [val for val in mylist_Obj if val in I_band],
	"obj_V": [val for val in mylist_Obj if val in V_band],
	"obj_Ikp": [val for val in mylist_Obj if val in Ikp]
}

csvFileNames=[]
for listName in megadict.keys():
        list = megadict[listName]
	i = len(csvFileNames)
	csvFileNames.append([])
	cvs_list=[]
	for item in list:
		pieces=item.split('\t')
		imname=pieces[0]
		cvs_list.append(imname)
	csvFileNames[i] =",".join(cvs_list)
			
if debug==True:
	for i in range(len(csvFileNames)):
		print i,megadict.keys()[i],":    ",csvFileNames[i]

FFB_csv=csvFileNames[7]
FFV_csv=csvFileNames[4]
FFI_csv=csvFileNames[1]
FFIkp_csv=csvFileNames[2]

objB_csv=csvFileNames[3]
objI_csv=csvFileNames[0]
objV_csv=csvFileNames[5] #empty
objIkp_csv=csvFileNames[6] #empty 

remove=raw_input("remove intermediate files and reduced_data directory? ('y' if script has been run before, 'n' if this is first time running) ")
if remove =="y":
	import shutil
	shutil.rmtree('reduced_data/')
	print "\nold directory deleted!"

	files = glob.glob('FF*')
	for f in files:
		os.remove(f)

FFB_combined=imcombine(FFB_csv,"FFB_combined.fit",combine='median',scale='mean',Stdout=1)
FFI_combined=imcombine(FFI_csv,"FFI_combined.fit",combine='median',scale='mean',Stdout=1)
FFV_combined=imcombine(FFV_csv,"FFV_combined.fit",combine='median',scale='mean',Stdout=1)
FFIkp_combined=imcombine(FFIkp_csv,"FFIkp_combined.fit",combine='median',scale='mean',Stdout=1)

print "\ncombined flat fields generated!"

Bmean=imstat("FFB_combined.fit",fields='mean',Stdout=1)
Imean=imstat("FFI_combined.fit",fields='mean',Stdout=1)
Vmean=imstat("FFV_combined.fit",fields='mean',Stdout=1)
Ikpmean=imstat("FFIkp_combined.fit",fields='mean',Stdout=1)

meanlist=[Bmean, Imean, Vmean, Ikpmean]
meanvallist=[]
for i in meanlist:
	meanvallist.append(float(i[1].strip()))

if debug==True:
	print meanvallist
	print Bmean, Imean, Vmean, Ikpmean

FFB_comb_norm=imarith("FFB_combined.fit","/",meanvallist[0],"FFB_comb_norm.fit",Stdout=1)
FFI_comb_norm=imarith("FFI_combined.fit","/",meanvallist[1],"FFI_comb_norm.fit",Stdout=1)
FFV_comb_norm=imarith("FFV_combined.fit","/",meanvallist[2],"FFV_comb_norm.fit",Stdout=1)
FFIkp_comb_norm=imarith("FFIkp_combined.fit","/",meanvallist[3],"FFIkp_comb_norm.fit",Stdout=1)

if debug==True:
	print "FF_comb_norm: ",FFB_comb_norm

print "\ncombined normalized flat fields generated!"

path=r'reduced_data/'
os.makedirs(path)
print "\nreduced data directory created!"

reduced_Bimages=imarith(objB_csv,"/","FFB_comb_norm.fit","reduced_data/objB_reduced001.fit,reduced_data/objB_reduced002.fit",Stdout=1)
print "\nreduced B images generated!"
reduced_Iimages=imarith(objI_csv,"/","FFI_comb_norm.fit","reduced_data/objI_reduced001.fit,reduced_data/objI_reduced002.fit",Stdout=1)
print "\nreduced I images generated!"

