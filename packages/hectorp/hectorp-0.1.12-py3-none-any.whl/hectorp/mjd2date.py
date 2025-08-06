# -*- coding: utf-8 -*-
#
# Simple MJD to date converter.
#
# This file is part of HectorP 0.1.12.
#
#  HectorP is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  any later version.
#
#  HectorP is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with HectorP. If not, see <http://www.gnu.org/licenses/>
#
# 14/2/2022 Machiel Bos, Santa Clara
#===============================================================================

import sys
from hectorp.my_calendar import compute_date

#===============================================================================
# Main program
#===============================================================================

def main():

    args = sys.argv[1:]

    if len(args)!=1:
        print("Correct input: mjd2date MJD\n");
        sys.exit()
    else:
        mjd = float(args[0])
        [year,month,day,hour,minute,second] = compute_date(mjd)
        print("year   : {0:4d}".format(year))
        print("month  : {0:4d}".format(month))
        print("day    : {0:4d}".format(day))
        print("hour   : {0:4d}".format(hour))
        print("minute : {0:4d}".format(minute))
        print("second : {0:f}".format(second))
        print("MJD    : {0:f}".format(mjd))
