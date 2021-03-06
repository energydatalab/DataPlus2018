""" 
geoToPix.py

Author: Tamasha Pathirathna
Organization: Duke University

Description: Script to pull pixel coordinates from the properties section of geojson files generated by pixToGeo.py. 
A json file containing the pixel coordinates is generated. The file is formatted to be read into pyimmannotate 
(an annotation tool create by Artem Streltsov). Developed for use in the Energy Infrastructure Map of the World project 
at Duke University.

Usage: Run this script in the directory that contains the geojson files to be converted and their associated tif images. 
Both the tif and geojson must have the same name before the extention. In practice, example.tif and example.geojson are 
input and example.json is created.

 """
import geojson
import json
import os
import gdal
import random

#run this in the directory that contains the geojson files 
jsonFiles = [f for f in os.listdir('.') if f.endswith('.geojson')]

#iterate through all geojson files in directory
#associated tif file with same filename must be available
for f in jsonFiles:
    imagePath = os.path.abspath(f[:-8] +".tif")
    data = geojson.load(open(f))
    dict = {'objects': [], 'type':[], 'label':[], 'width/height': [1300, 1300], 'lineColor':[], 'imagePath':imagePath}
    colordict = {}
    name = f[:-8]
    
    
    for features in data['features']:
        
        if(features['geometry']['type'] == "MultiLineString"):
            dict['type'].append('Line')
        else:
            dict['type'].append(features['geometry']['type'])
        
        
        label = features['properties']['label']
        dict['label'].append(label)
        
        dict['objects'].append(features['properties']['pixel_coordinates'])
        
        #generate random color to be associated with each label
        if features['properties']['label'] in colordict.keys():
            dict['lineColor'].append(colordict[label])
        else:
            color = "%06x" % random.randint(0, 0xFFFFFF)
            colordict[label] = '#' + color
            dict['lineColor'].append(colordict[label])
            
        filename = name+"_2.json"
        with open(filename,'w') as f:
            json.dump(dict, f, ensure_ascii=True, indent=2)
