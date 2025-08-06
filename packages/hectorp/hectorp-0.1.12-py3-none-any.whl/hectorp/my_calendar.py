# -*- coding: utf-8 -*-
#
# This file is part of HectorP 0.1.12.
#
# HectorP is free software: you can redistribute it and/or modify it under the 
# terms of the GNU General Public License as published by the Free Software 
# Foundation, either version 3 of the License, or (at your option) any later 
# version.
#
# HectorP is distributed in the hope that it will be useful, but WITHOUT ANY 
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with 
# HectorP. If not, see <https://www.gnu.org/licenses/>.
#
# 29/12/2021  Machiel Bos, Santa Clara
#==============================================================================

import os
import sys
import math

#==============================================================================
# Subroutines
#==============================================================================


#---------------------
def compute_date(mjd):
#---------------------
    """ Compute the Modified Julian Date

    Args:
        mjd : modified julian date

    Returns:
        year (int)
        month (int)
        day (int)
        hour (int)
        minute (int)
        second (float)
    """

    jul = int(mjd) + 2400001
    l = jul+68569;
    n = 4*l//146097;
    l = l-(146097*n+3)//4;
    i = 4000*(l+1)//1461001;
    l = l-1461*i//4+31;
    j = 80*l//2447;
    k = l-2447*j//80;
    l = j//11;
    j = j+2-12*l;
    i = 100*(n-49)+i+l;

    year  = i
    month = j
    day   = k

    f      = 24.0*(mjd-math.floor(mjd))
    hour   = int(f)
    f      = 60.0*(f - hour)
    minute = int(f)
    second = 60.0*(f - minute)

    return [year,month,day,hour,minute,second]



#--------------------------------------------------
def compute_mjd(year,month,day,hour,minute,second):
#--------------------------------------------------
    """ Compute the Modified Julian Date

    Args:
        year (int)
        month (int)
        day (int)
        hour (int)
        minute (int)
        second (float)

    Returns:
        mjd : modified julian date
    """

    mjd = 367*year - int(7*(year+int((month+9)/12))/4) + int(275*month/9) + \
                                                      day + 1721014 - 2400001

    mjd += (hour + (minute + second/60.0)/60.0)/24.0

    return mjd


#===============================================================================
# Main program
#===============================================================================

def main():

    args = sys.argv[1:]

    if len(args!=6):
        print("Correct input: date2MJD year month day hour minute second")
        sys.exit()
    else:
        year  = int(args[0])
        month = int(args[1])
        day   = int(args[2])
        hour  = int(args[3])
        minute= int(args[4])
        second= float(args[5])
        mjd = compute_mjd(year,month,day,hour,minute,second)
        print("year   : {0:4d}".format(year))
        print("month  : {0:4d}".format(month))
        print("day    : {0:4d}".format(day))
        print("hour   : {0:4d}".format(hour))
        print("minute : {0:4d}".format(minute))
        print("second : {0:f}".format(second))
        print("MJD    : {0:f}".format(mjd))
