""" 
pixToGeo.py

Author: Tamasha Pathirathna
Organization: Duke University

Description: Converts pixel coordinate annotations retained in a json file to geocoordinates. 
A geojson file containing the geocoordiantes as well as image metadata is created. Developed 
for use in the Energy Infrastructure Map of the World project at Duke University.

Usage: Run this script in the directory containing the tiff files and their associated json files.
The files should share the same name prior to the extention (example.tif, example.json). A geojson
with the same name will be generated (example.geojson).

 """

from osgeo import gdal
from osgeo import ogr
from osgeo import osr
from PIL import Image
from geojson import Feature, LineString, FeatureCollection, Polygon, GeometryCollection
import geojson
import json
import os
import pandas as pd

#run this is in the directory that contains both the tiff files and their associated json files
tiffFiles = [f for f in os.listdir('.') if f.endswith(".tif")]

def createGeojson(data, name, imageLat, imageLong, pix, projection):
    col = ['coordinate', 'type', 'label']
    df = pd.DataFrame(data, columns = col)
    
    geofilename = name + ".geojson"
    filenameData = geofilename.split("_")
    
    features=[]
    for name, row in df.iterrows():
        coords_pol=row['coordinate']
        if row['type']=='Polygon':
            if coords_pol[-1]!=coords_pol[0]:
                coords_pol.append(coords_pol[0])
            features.append(geojson.Feature(properties={'label': row['label'], 'filename': geofilename, 'Country':filenameData[0], 'City':filenameData[1], 'Image GeoCoordinates': [imageLat, imageLong], 'Pixel Coordinates': pix, 'Projection': projection}, geometry=geojson.Polygon([coords_pol])))
        elif row['type']=='Line':
            features.append(geojson.Feature(properties = {'label': row['label'], 'filename': geofilename, 'Country':filenameData[0], 'City':filenameData[1], 'Image GeoCoordinates': [imageLat, imageLong], 'Pixel Coordinates': pix, 'Projection': projection}, geometry=geojson.MultiLineString([coords_pol])))
        
    f_coll=geojson.FeatureCollection(features)
    
    with open(geofilename, 'w') as f:
        json.dump(f_coll,f, indent = 2)


for f in tiffFiles:
    name = f[:-4]
    filename = name +".json"
    jsonFile = json.load(open(filename))
    pointsList = jsonFile['objects']
    typeList = jsonFile['type']
    labelList = jsonFile['label']
    index = 0

    image = gdal.Open(f) 
    transform = image.GetGeoTransform()

    #input upper left coordinates of image to convert to WGS84 projection
    point = ogr.Geometry(ogr.wkbPoint)
    point.AddPoint(transform[0], transform[3])
    
    #calculate lower right coordinates
    lrx = transform[0] + transform[1]*image.RasterXSize
    lry = transform[3] + transform[5]*image.RasterYSize
    
    #input lower right coordinates to convert to WGS84 projection
    point2 = ogr.Geometry(ogr.wkbPoint)
    point2.AddPoint(lrx, lry)
    
    source = osr.SpatialReference()
    source.ImportFromWkt(image.GetProjection())
    
    target = osr.SpatialReference()
    target.ImportFromEPSG(4326)
    
    transform = osr.CoordinateTransformation(source, target)
    point.Transform(transform)
    point2.Transform(transform)
    
    #upper left and lower right coordinates as WGS84 projection
    ulx = point.GetX()
    uly = point.GetY()
    lrx = point2.GetX()
    lry = point2.GetY()
    
    pixelWidth = (lrx -ulx)/image.RasterXSize
    pixelHeight = (lry - uly)/image.RasterYSize

    data1 = []
    data = []
    
    #convert all pixel coordinates to geocoordinates 
    for w in pointsList:
        currentPoints = pointsList[index]
        currentType = typeList[index]
        currentLabel = labelList[index]
            
        index = index + 1

        for point in currentPoints:
            x = ulx + pixelWidth*point[0]
            y = uly + pixelHeight*point[1]
            data1.append([x,y])
        data.append([data1, currentType, currentLabel])
        data1 = []
        
    #dump data into geojson
    createGeojson(data, name, ulx, uly, pointsList, image.GetProjection())