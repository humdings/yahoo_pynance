# -*- coding: utf-8 -*-
"""
Created on Fri Dec 13 13:41:42 2013

@author: David Edwards
"""
import datetime


def str_to_dt(date):
    yr = int(date[0:4])
    mo = int(date[5:7])
    day = int(date[8:10])
    return datetime.datetime(yr,mo, day)
