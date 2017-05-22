#coding:utf-8

# from base import *

# import threading
import math

METERS_PER_MINUTE= 1860.0
METERS_PER_DEGREE= METERS_PER_MINUTE*60*1.0

"""
#define sw_PI	3.1415926
#define sw_METERS_PER_MINUTE	(1860.0)
#define sw_METERS_PER_DEGREE	(sw_METERS_PER_MINUTE*60*1.0)
#define sw_METERS_PER_SECOND	(sw_METERS_PER_MINUTE/60*1.0)

#define sw_METRIC_DPI	96.0  //每个英寸包含96个像素
#define sw_METERS_PER_PIXEL (0.0254/sw_METRIC_DPI) //每个象素表示的实际长度，单位:米

0.1 degress = 1860.0 * 6 = 11 km

"""
# y ( 0-15 ) ,x (16 - 31)
def CELL_INDEX(x,y):
    # return ((x & 0xf5fff)<<16)| (y&0xffff)
    # return ((x & 0xf5fff)<<16)| (y&0xffff)
    return "%05d,%05d"%(x,y)

def distance(a,b):
    return math.sqrt( math.pow(b[0]-a[0],2) + math.pow( b[1]-a[1],2) )


def isPtInRect(rc, pt):
    if pt[0] > rc[0] and pt[0] < (rc[0] + rc[2]) and pt[1] > rc[1] and pt[1] < (rc[1] + rc[3]):
        return True
    return False

class MapCell:
    def __init__(self,grid,x,y):
        self.grid = grid
        self.x = x          # 网格索引编号
        self.y = y          # 网格索引编号
        self.mos = {}       # 位置对象

    def index(self):
        return CELL_INDEX(self.x,self.y)

    def putObject(self,mo):
        """移动对象关联到网格块
            同一个grid中，只能出现在一个cell中
        """
        # print 'mo put into:',self.index(), ' in grid:',self.grid.name

        # self.mos[ mo.getId()] = mo

        tag = 'grid-'+self.grid.name
        cell = mo.getTag(tag)
        if cell and cell is not self:
            cell.removeObject(mo)

        self.mos[mo.getId()] = mo
        mo.setTag(tag, self)

    def removeObject(self,mo):
        if self.mos.has_key(mo.getId()):
            del self.mos[mo.getId()]

    def rect(self):
        x = self.x*self.grid.cellsize[0] + self.grid.origin()[0]
        y = self.y*self.grid.cellsize[1] + self.grid.origin()[1]
        return x,y,self.grid.cellsize[0],self.grid.cellsize[1]

    def center(self):
        rc = self.rect()
        cx = rc[0] + rc[2]/2.0
        cy = rc[1] + rc[3]/3.0
        return cx,cy

    def size(self):
        return self.grid.cellsize

    @staticmethod
    def isPtInRect(rc,pt):
        if pt[0]>rc[0] and pt[0] < rc[0]+rc[2] and pt[1]>rc[1] and pt[1] < rc[1]+rc[3]:
            return True
        return False

    def isPointIn(self,pt):
        rc = self.rect()
        return MapCell.isPtInRect(rc,pt)

    def spatialQueryByRect(self,rect,result,allow=lambda _:False):
        """

        :param rect: (x,y,w,h)
        :param result:
        :return:
        """
        for k, mo in self.mos.items():
            x, y = mo.getLocation().lon, mo.getLocation().lat
            if MapCell.isPtInRect( rect,(x, y)):
                if allow(mo):
                    result.append(mo)

    def spatialQueryByCircle(self,circle,result,allow=lambda _:True):
        """
        :param circle: (x,y,radius)
        :param result:
        :return:
        """
        for k,mo in self.mos.items():
            x,y = mo.getLocation().lon,mo.getLocation().lat
            cx,cy = circle[0],circle[1]
            radius = circle[2]
            if distance((x,y),(cx,cy) ) <= radius:
                if allow(mo):
                    result.append(mo)


class GlobalMap:
    def __init__(self,name,cell_size=(0.5,0.5),region=(70,10,70,50)):
        self.name = name
        self.cellsize = cell_size   # 网格块规格
        self.region = region        # 原点
        self.cells={}               # 网格块列表
        self.initdata()
        # self.mtxcells = threading.Lock()

    def origin(self):
        return self.region[:2]

    def width(self):
        return self.region[2]

    def height(self):
        return self.region[3]

    def getCellIndex(self,x,y):
        """
        :param x: lon
        :param y: lat
        :return:
        """
        distx = x - self.origin()[0]
        disty = y - self.origin()[1]
        idx_x = distx // self.cellsize[0]
        idx_y = disty // self.cellsize[1]
        return int(idx_x), int(idx_y)

    def getCell(self,x,y):
        """
        :param x: lon
        :param y: lat
        :return:
        """
        x,y = self.getCellIndex(x,y)
        cellid = CELL_INDEX(x,y)
        # self.mtxcells.acquire()
        cell = self.cells.get(cellid)
        # self.mtxcells.release()
        return cell

    def getCells(self,rc):
        x1,y1 = self.getCellIndex(rc[0],rc[1])
        x2,y2 = self.getCellIndex(rc[0] + rc[2], rc[1] + rc[3])
        cells =[]
        x = x1
        while y1<=y2:
            x1 = x
            while x1<=x2:
                # self.mtxcells.acquire()
                cellid = CELL_INDEX(x1,y1)
                cell = self.cells.get(cellid)
                # self.mtxcells.release()
                if cell:
                    cells.append(cell)
                else:
                    # print 'cell is null:',cellid
                    pass
                x1+=1
            y1+=1
        #
        return cells

    # def spatialQuery(self,case):
    #     c = case
    #     rc = (c.rect.x,c.rect.y,c.rect.width,c.rect.height)
    #     if c.type == SpatialQueryGeomType.ByCircle:
    #         rc = (  c.circle.center.lon - c.radius,
    #                 c.circle.center.lat - c.radius,
    #                 c.circle.radius*2,
    #                 c.circle.radius*2)
    #     locs = []
    #     cells = self.getCells(rc)
    #     for cell in cells:
    #         cell.spatialQuery(case,locs)
    #     # sort ,or limit
    #     #距离排序
    #     cxy = ()
    #     if c.type == SpatialQueryGeomType.ByCircle:
    #         cxy = (c.circle.center.lon,c.circle.center.lat)
    #     else:
    #         cxy = ( c.rect.x+c.rect.width/2.0, c.rect.y+c.rect.height/2.0 )
    #
    #     sorted(locs,cmp=lambda a,b:
    #         distance( (a.loc.gps.loc.lon,a.loc.gps.loc.lon),cxy) > distance( (b.loc.gps.loc.lon,b.loc.gps.loc.lon),cxy)
    #         )
    #     #limit限制
    #     locs = locs[:case.limit]
    #     return locs

    # def spatialQueryByRect(self,rect):
    #     # c = case
    #     rc = rect
    #     cells = self.getCells(rc)
    #     for cell in cells:
    #         cell.spatialQuery(case,locs)
    #     # sort ,or limit
    #     #距离排序
    #     cxy = ()
    #     if c.type == SpatialQueryGeomType.ByCircle:
    #         cxy = (c.circle.center.lon,c.circle.center.lat)
    #     else:
    #         cxy = ( c.rect.x+c.rect.width/2.0, c.rect.y+c.rect.height/2.0 )
    #
    #     sorted(locs,cmp=lambda a,b:
    #         distance( (a.loc.gps.loc.lon,a.loc.gps.loc.lon),cxy) > distance( (b.loc.gps.loc.lon,b.loc.gps.loc.lon),cxy)
    #         )
    #     #limit限制
    #     locs = locs[:case.limit]
    #     return locs

    def update(self,d):
        x,y = d.loc.gps.loc.lon,d.loc.gps.loc.lat
        cell = self.getCell(x,y)
        if cell:
            cell.update(d)
        else:
            print 'location is out of bound of map!'



    def initdata(self):
        x,y,w,h = self.region
        x1,y1 = self.getCellIndex(x,y)
        x2,y2 = self.getCellIndex(x + w, y + h)
        x = x1
        while y1<=y2:
            x1 = x
            while x1<=x2:
                cellid = CELL_INDEX(x1,y1)
                cell = MapCell(self,x1,y1)
                self.cells[cellid] = cell
                x1+=1
            y1+=1


if __name__ == '__main__':
    rect = [127.097802, 38.484503, 0.019510999999994283, 0.007569000000003712]
    map = GlobalMap('test')
    x,y= map.getCellIndex(127.097802, 38.484503)
    cell = map.getCell(127.097802, 38.484503)
    print x,y
    print cell.rect()

