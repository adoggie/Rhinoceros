#coding:utf-8

#
# SQL_LOCATION ="""
#
# CREATE TABLE mo_buffers
# (
#     moid TEXT PRIMARY KEY NOT NULL,
#     data TEXT,
#     time TEXT NOT NULL
# );
# CREATE  INDEX mo_buffers_time_index ON mo_buffers (time);
# CREATE UNIQUE INDEX mo_buffers_moid_uindex ON mo_buffers (moid);
#
# """

class SpatialQueryGeomType:
    ByCircle = 1
    ByRect = 2

class VehicleStatus:
    RUNNING = 1
    STOPPED = 2
    OFFLINE = 3

OFFLINE_TIME = 10*60 # 指定离线时间