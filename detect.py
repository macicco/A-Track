# -*- coding: utf-8 -*-
"""
Created on Sat Feb 22 19:43:14 2015

@author: ykilic
"""

import math
import glob
import os
import pyfits
import time
import pandas as pd
import itertools as it

try:
    import numpy as np
except ImportError:
    print "Did you install pandas?"
    raise SystemExit

try:
    import plot as pt
except ImportError:
    print "Can not load plot. Do you have plot.py?"
    raise SystemExit


class Detect:
    """
    MOD's detection class.
                
    """
    def distance(self, xcoor0, ycoor0, xcoor1, ycoor1):
        """
        distance(xcoor0, ycoor0, xcoor1, ycoor1) -> float
        Returns distence between two points.
        
        @param xcoor0: x coordinate for first point
        @type xcoor0: float, integer
        @param ycoor0: y coordinate for first point
        @type ycoor0: float, integer
        @param xcoor1: x coordinate for second point
        @type xcoor1: float, integer
        @param ycoor1: y coordinate for second point
        @type ycoor1: float, integer
        @return: float
        """
        dist = math.sqrt((ycoor1 - ycoor0)**2 + (xcoor1 - xcoor0)**2)
        return dist

    def finalCheck(self, coor0, coor1, coor2):
        longestt = self.longest(coor0, coor1, coor2)
        if longestt == (coor0, coor2, coor1):
          return True
        else:
          return False

    def isClose(self, coor1, coor2, r):
        """
        isClose(coor1, coor2, r) -> boolean
        Returns true and false if the second point is in the selected r radius.
        
        @param coor1: first point's x and y coordinates
        @type coor1: list
        @param coor2: second point's x and y coordinates
        @type coor2: list
        @param r: radius for search point
        @type r: float, integer
        @return: boolean
        """
        d = self.distance(coor1[0], coor1[1], coor2[0], coor2[1])
        if float(d) <= float(r):
            return True
        else:
            return False
    
    
    def longest(self, coor1, coor2, coor3):
        """
        longest(coor1, coor2, coor3) -> list
        Returns longest side of triangle
        
        @param coor1: first point's x and y coordinates
        @type coor1: list
        @param coor2: second point's x and y coordinates
        @type coor2: list
        @param coor3: third point's x and y coordinates
        @type coor3: list
        @return: list
        """

        d12 = self.distance(coor1[0], coor1[1], coor2[0], coor2[1])
        d13 = self.distance(coor1[0], coor1[1], coor3[0], coor3[1])
        d23 = self.distance(coor3[0], coor3[1], coor2[0], coor2[1])
        lis = [d12, d23, d13]
        ref = lis[0]
        index = 0
                
        for n, i in enumerate(lis):
            if ref < i:
                ref = i
                index = n
        
        if index == 0:
            return coor1, coor2, coor3
        elif index == 1:
            return coor2, coor3, coor1
        elif index == 2:
            return coor1, coor3, coor2
    
    def height(self, line, xy):
        """
        height(line, xy) -> float
        Returns shortest distance a point to a line.
        
        @param line: line's coordinates as [[x1, y1], [x2, y2]]
        @type line: list
        @param xy: coordinates of a point (x, y)
        @type xy: list
        @return: float
        """
        x0 = line[0][0]
        y0 = line[0][1]
        x1 = line[1][0]
        y1 = line[1][1]
        x2 = xy[0]
        y2 = xy[1]
        try:
            h = math.fabs((x1 - x0)*y2 + (y0 - y1)*x2 + x0*y1 - x1*y0) / math.sqrt(math.pow(x1 - x0, 2) + math.pow(y1 -y0, 2))
        except ZeroDivisionError:
            h = 0
        return h

    def detectstrayobjects(self, reference_cat, star_cat, target_folder, min_fwhm=1, max_fwhm=7, max_flux=500000, elongation=1.8, snrsigma=15, basepar=0.37):
        """
        Reads given ordered (corrected) coordinate file and detect stray objects in "starcat.txt".
        
        @param reference_cat: Ordered (corrected) star catalogue file for one image.
        @type reference_cat: Text file object.
        @param star_cat: Ordered (corrected) star catalogue file for all image.
        @type star_cat: Text file object...
                    
        """
        catfile = os.path.basename(reference_cat)
        h_catfile, e_catfile = catfile.split(".")
        
        if e_catfile == "pysexcat":
            ref_np = np.genfromtxt(reference_cat, delimiter=None, comments='#')
            star_np = np.genfromtxt(star_cat, delimiter=None, comments='#')
            
            reference = pd.DataFrame.from_records(ref_np, columns=["id_flags", "x", "y", "flux", "background", "fwhm", "elongation", "fluxerr"])
            star_catalogue = pd.DataFrame.from_records(star_np, columns=["id_flags", "x", "y", "flux", "background", "fwhm", "elongation", "fluxerr"])
            
            refcat_all = reference[((reference.id_flags == 0) | (reference.id_flags == 1) | (reference.id_flags == 2) | (reference.id_flags == 3) | (reference.id_flags == 16)) & (reference.flux <= max_flux) & (reference.fwhm <= max_fwhm) & \
            ((reference.flux / reference.fluxerr) > snrsigma) & (reference.fwhm >= min_fwhm) & (reference.elongation <= elongation)]
            starcat_all = star_catalogue[((star_catalogue.id_flags == 0) | (star_catalogue.id_flags == 1) | (star_catalogue.id_flags == 2) | (star_catalogue.id_flags == 3) | (star_catalogue.id_flags == 16)) & (star_catalogue.flux <= max_flux) & (star_catalogue.fwhm <= max_fwhm) & \
            ((star_catalogue.flux / star_catalogue.fluxerr) > snrsigma) & (star_catalogue.fwhm >= min_fwhm) & (star_catalogue.elongation <= elongation)]
            
            refcat = refcat_all[["id_flags", "x", "y", "flux", "background"]]
            refcat = refcat.reset_index(drop=True)
            starcat = starcat_all[["id_flags", "x", "y", "flux", "background"]]
            starcat = starcat.reset_index(drop=True)
            
            # flags or id, first column is not important, i added first column for just check.
        else:
            refcat = pd.read_csv(reference_cat, sep=" ", names=["id_flags", "x", "y", "flux", "background"], header=0)
            starcat = pd.read_csv(star_cat, sep=" ", names=["id_flags", "x", "y", "flux", "background"], header=0)
        
        strayobjectlist = pd.DataFrame(columns=["id_flags", "x", "y", "flux", "background"])
        for i in range(len(refcat.x)):
            if len(starcat[((starcat.x - refcat.x[i])**2 + (starcat.y - refcat.y[i])**2)**0.5 <= basepar]) < 2:
                strayobjectlist = strayobjectlist.append(refcat.iloc[i], ignore_index=True)

        if os.path.exists(target_folder):
            pass
        else:
            os.mkdir(target_folder)        
        
        strayobjectlist.to_csv("%s/stray_%s.txt" %(target_folder, h_catfile), index = False)
        return strayobjectlist

    def detectlines(self, fits_path, catdir, output_figure, basepar=0.37, heightpar=0.5, pixel_scale=0.31, vmax=0.03, radiusSigma = 1):
        """
        
        Reads given ordered (corrected) coordinate file and detect lines with randomized algorithm.
        
        @param ordered_cats: Ordered (corrected) star catalogues folder.
        @type ordered_cats: Directory object.
        @param output_figure: Plot figure path to save.
        @type output_figure: PNG object.
        @param basepar: The length of the base.
        @type basepar: Float                    
        @param heightpar: The length of the triangle's height.
        @type heightpar: Float
        @param areapar: The area of triangle.
        @type areapar: Float
        """ 
        fitsfiles = sorted(glob.glob("%s/*.fit*" %(fits_path)))
        starcat = sorted(glob.glob("%s/*affineremap.txt" %(catdir)))
        
        lst = []
        fileidlist = []
        can = []
        res = []
        pointid = 0
        
        #all files copying to list
        for fileid, objctlist in enumerate(starcat):
            objtcat = pd.read_csv(objctlist, sep=",", names = ["id_flags", "x", "y", "flux", "background"], header=0)
            if not objtcat.empty:
                lst.append(objtcat.values)
                fileidlist.append(fileid)
                
        #calculation of a triangle's area and checking points on a same line.
        
        combinatedfileids = it.combinations(fileidlist, 3)
        
        for cyc, selectedfileids in enumerate(list(combinatedfileids)):
        #for i in xrange(len(lst)-2):
            fileid_i, fileid_j, fileid_k = selectedfileids
            print "Searching lines in %s., %s., %s. (%s) files" %(fileid_i, fileid_j, fileid_k, cyc)
            hdulist1 = pyfits.open(fitsfiles[fileid_i])
            hdulist2 = pyfits.open(fitsfiles[fileid_j])
            hdulist3 = pyfits.open(fitsfiles[fileid_k])
            xbin = hdulist1[0].header['xbinning']
            ybin = hdulist1[0].header['ybinning']
            obsdate1 = hdulist1[0].header['date-obs']
            exptime1 = hdulist1[0].header['exptime']
            obsdate2 = hdulist2[0].header['date-obs']
            exptime2 = hdulist2[0].header['exptime']
            obsdate3 = hdulist3[0].header['date-obs']
            exptime3 = hdulist3[0].header['exptime']
            otime1 =  time.strptime(obsdate1, "%Y-%m-%dT%H:%M:%S.%f")
            otime2 =  time.strptime(obsdate2, "%Y-%m-%dT%H:%M:%S.%f")
            otime3 =  time.strptime(obsdate3, "%Y-%m-%dT%H:%M:%S.%f")
            radius =  (time.mktime(otime2) - time.mktime(otime1) + (exptime2 - exptime1) / 2) * vmax / (pixel_scale * xbin)
            radius2 =  (time.mktime(otime3) - time.mktime(otime2) + (exptime3 - exptime2) / 2) * vmax / (pixel_scale * xbin)
            for u in xrange(len(lst[fileid_i])):
                for z in xrange(len(lst[fileid_j])):
                    #ilk çift nokta seçiliyor
                    absRadius1 = self.distance(lst[fileid_i][u][1], lst[fileid_i][u][2], lst[fileid_j][z][1], lst[fileid_j][z][2])
                    deltaobs1 = (time.mktime(otime2) - time.mktime(otime1)) + (exptime2 - exptime1) / 2
                    if self.isClose(lst[fileid_i][u, [1,2]], lst[fileid_j][z, [1,2]], radius):
                        for x in xrange(len(lst[fileid_k])):
                            absRadius2 = self.distance(lst[fileid_j][z][1], lst[fileid_j][z][2], lst[fileid_k][x][1], lst[fileid_k][x][2])
                            deltaobs2 =  (time.mktime(otime3) - time.mktime(otime2)) + (exptime3 - exptime2) / 2
                            if self.isClose(lst[fileid_j][z, [1,2]], lst[fileid_k][x, [1,2]], radius2):
                                if ((deltaobs2 * absRadius1 / deltaobs1) - radiusSigma) <= absRadius2 and ((deltaobs2 * absRadius1 / deltaobs1) + radiusSigma) >= absRadius2:                                             
                                    base = self.longest(lst[fileid_i][u, [1,2]], lst[fileid_j][z, [1,2]], lst[fileid_k][x, [1,2]])
                                    hei = self.height(base[:-1], base[-1])
                                    lengh = self.distance(base[0][0], base[0][1], base[1][0], base[1][1])
                                    if lengh > basepar * 1.5 and hei < heightpar:
                                        p1 = [lst[fileid_i][u][1], lst[fileid_i][u][2]]
                                        p2 = [lst[fileid_j][z][1], lst[fileid_j][z][2]]
                                        p3 = [lst[fileid_k][x][1], lst[fileid_k][x][2]]
                                     
                                        if self.finalCheck(p1, p2, p3):
                                            if len(res) == 0:
                                                pointid = 1
                                                res.append([fileid_i,lst[fileid_i][u][0], lst[fileid_i][u][1], lst[fileid_i][u][2], lst[fileid_i][u][3], lst[fileid_i][u][4], pointid])
                                                res.append([fileid_j, lst[fileid_j][z][0], lst[fileid_j][z][1], lst[fileid_j][z][2], lst[fileid_j][z][3], lst[fileid_j][z][4], pointid])
                                                res.append([fileid_k, lst[fileid_k][x][0], lst[fileid_k][x][1], lst[fileid_k][x][2], lst[fileid_k][x][3], lst[fileid_k][x][4], pointid])
                                            else:
                                                if not [s1 for s1 in res if s1[2:4] == p1]:
                                                    pointid = np.amax(np.asarray([row[6] for row in res])) + 1
                                                    res.append([fileid_i,lst[fileid_i][u][0], lst[fileid_i][u][1], lst[fileid_i][u][2], lst[fileid_i][u][3], lst[fileid_i][u][4], pointid])
                                                    res.append([fileid_j, lst[fileid_j][z][0], lst[fileid_j][z][1], lst[fileid_j][z][2], lst[fileid_j][z][3], lst[fileid_j][z][4], pointid])
                                                    res.append([fileid_k, lst[fileid_k][x][0], lst[fileid_k][x][1], lst[fileid_k][x][2], lst[fileid_k][x][3], lst[fileid_k][x][4], pointid])
                                                else:
                                                    indx1 = [row[6] for row in [s1 for s1 in res if s1[2:4] == p1]]
                                                    if not [s2 for s2 in res if s2[2:4] == p2]:
                                                        pointid = np.amax(np.asarray([row[6] for row in res])) + 1
                                                        res.append([fileid_i,lst[fileid_i][u][0], lst[fileid_i][u][1], lst[fileid_i][u][2], lst[fileid_i][u][3], lst[fileid_i][u][4], pointid])
                                                        res.append([fileid_j, lst[fileid_j][z][0], lst[fileid_j][z][1], lst[fileid_j][z][2], lst[fileid_j][z][3], lst[fileid_j][z][4], pointid])
                                                        res.append([fileid_k, lst[fileid_k][x][0], lst[fileid_k][x][1], lst[fileid_k][x][2], lst[fileid_k][x][3], lst[fileid_k][x][4], pointid])
                                                    else:
                                                        indx2 = [row[6] for row in [s2 for s2 in res if s2[2:4] == p2]]
                                                        print "==========="
                                                        print indx1
                                                        print indx2
                                                        
                                                        for k in indx1:
                                                            for s in indx2:
                                                                if k == s:
                                                                    oldpointsid = k
                                                                else:
                                                                    print "hataaaaaaaaaaaaa: ", k, s
                                                                    if k == -1:
                                                                        oldpointsid = s
                                                                    elif s ==-1:
                                                                        oldpointsid = k
                                                                    else:
                                                                        if oldpointsid != -1 or oldpointsid != 0:
                                                                            oldpointsid = -1
                                                        if oldpointsid != -1 :
                                                            res.append([fileid_k, lst[fileid_k][x][0], lst[fileid_k][x][1], lst[fileid_k][x][2], lst[fileid_k][x][3], lst[fileid_k][x][4], pointid])
                                                        print "==========="
                                        else:
                                            print "final check failed"

        if res:
            print np.asarray(res)
            return np.asarray(res)
        else:
            print "No lines detected!"
            return False
