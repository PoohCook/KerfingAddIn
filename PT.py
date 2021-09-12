import adsk.core, adsk.fusion, adsk.cam
from . import NS

class ProfileTools():
    def __init__(self) -> None:
        pass

    def getIntersections(self, line, curves):
        points = adsk.core.ObjectCollection.create()
        for i in range(curves.count):
            curve = curves.item(i).geometry
            pnts = line.intersectWithCurve(curve)
            for j in range(pnts.count):
                c = pnts.item(j)
                for k in range(points.count):
                    e = points.item(k)
                    if e.x == c.x and e.y == c.y and e.z == c.z:
                        c = None
                        break
                if c: 
                    points.add(c)

        return points

    def getOutsidePoint(self, profile, max=True):
        if max:
            outerPoint = profile.boundingBox.maxPoint.copy()
            offset = adsk.core.Vector3D.create(0.1,0.1,0)
        else:
            outerPoint = profile.boundingBox.minPoint.copy()
            offset = adsk.core.Vector3D.create(-0.1,-0.1,0)
        outerPoint.translateBy(offset)
        return outerPoint
            
    def findIntersections(self, fromPoint, profile ):
        profile = adsk.fusion.Profile.cast(profile)
        outerPoint = self.getOutsidePoint(profile, max=True)
        pCurves = profile.profileLoops.item(0).profileCurves
        line = adsk.core.Line3D.create(outerPoint, fromPoint)
        points = self.getIntersections(line, pCurves)
        if points.count == 0:
            outerPoint = self.getOutsidePoint(profile, max=False)
            line = adsk.core.Line3D.create(outerPoint, fromPoint)
            points = self.getIntersections(line, pCurves)

        # don't beleive it is possible in euclidian space for not found second time
        return points

    def midPoint(self, pnt0, pnt1):
        ax = (pnt0.x + pnt1.x) / 2
        ay = (pnt0.y + pnt1.y) / 2
        az = (pnt0.z + pnt1.z) / 2
    
        return adsk.core.Point3D.create(ax, ay, az)

    def findInsidePoint(self, profile ):
        # best guesss at point inside
        inside = profile.areaProperties().centroid
        
        for i in range(10):
            points = self.findIntersections(inside, profile)
            # if number of intersecting points is odd, the point is inside
            if (points.count % 2) == 1:
                return inside
            #else guess at new inside point
            inside = self.midPoint(points.item(0), points.item(1))
            
        return None

    def containsProfile(self, outer, profile):
        contains = False
        insidePnt = self.findInsidePoint( profile)
        if insidePnt:
            points = self.findIntersections(insidePnt, outer)
            # if number of intersecting points is odd, the profile is inside
            if (points.count % 2) == 1:
                contains = True

        return contains

    def offsetProfiles(self, topProfile, kerf_width, deleteProfiles=False):
        sketch = adsk.fusion.Sketch.cast(topProfile.parentSketch)
        pCurves = topProfile.profileLoops.item(0).profileCurves
        kerfs = [NS.Namespace(
            curve=pCurves.item(0).sketchEntity, 
            point=self.findInsidePoint(topProfile),
            offset = -kerf_width
        )]

        for i in range(sketch.profiles.count):
            profile = sketch.profiles.item(i)
            if  profile != topProfile and self.containsProfile(topProfile, profile):

                pCurves = profile.profileLoops.item(0).profileCurves
                kerfs.append(NS.Namespace(
                    curve=pCurves.item(0).sketchEntity, 
                    point=self.findInsidePoint(profile),
                    offset = kerf_width
                ))

        for kerf in kerfs:
            curves = sketch.findConnectedCurves(kerf.curve)
            sketch.offset(curves, kerf.point, kerf.offset)

            if deleteProfiles:
                for i in range(curves.count):
                    curves.item(i).deleteMe()

            curves.clear()
    
        
