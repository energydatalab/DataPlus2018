'''
multiclassmask.py

Converts CSV file of annotations into multiclass mask for input into machine learning models
Includes option to output mask as tif and/or npz file
Simply run the script ('python multiclassmask.py')

Author: Xiaolan You & Artem Streltsov
Group: Duke Data+ and Energy Initiative
Date: July 28, 2018
'''

import pandas as pd
import numpy as np
import json
from skimage.draw import polygon, line
from scipy.misc import imsave
from PyQt5.QtWidgets import QFileDialog, QApplication
from PIL import Image
import pickle

# manually encode categories here
labelencoder = {
	'DT':1,
	'DL':2,
	'TT':3,
	'TL':4,
	'OT':5,
	'OL':6,
	'SS':7
}

def checkbounds(cc,rr,size_x, size_y):
    cc=np.maximum(np.minimum(cc,size_x),0)
    rr=np.maximum(np.minimum(rr,size_y),0)
    return cc,rr

def produce_mask(path):
	df=pd.read_csv(path)
	img=np.zeros((df['width'][0], df['height'][0]))
	for name,group in df.groupby('Object'):
		label=group['Label'].values[0]
		# ---- following specific to this project ----
		if label not in labelencoder.keys():
			if label[1]=='T':
				label_multiclass=labelencoder['OT']
			else:
				label_multiclass=labelencoder['OL']
		# ---------
		else:
			label_multiclass=labelencoder[label]

		if group['Type'].values[0]=='Polygon':
			cc,rr=polygon(group['X'].values, group['Y'].values)
			cc,rr=checkbounds(cc,rr,df['width'][0]-1,df['height'][0]-1)
			img[rr,cc]=label_multiclass
		elif group['Type'].values[0]=='Line':
			for j in range(group.shape[0]-1):
				r0, c0 = int(group['X'].values[j]), int(group['Y'].values[j])
				r1, c1 = int(group['X'].values[j+1]), int(group['Y'].values[j+1])
				cc,rr=line(r0, c0, r1, c1)
				cc,rr=checkbounds(cc,rr,df['width'][0]-1,df['height'][0]-1)
				img[rr,cc]=label_multiclass
		else:
			img[int(group['X']),int(group['Y'])]=label_multiclass

	# to save as npz file
	# np.savez_compressed(path[:-4], img)

	# to save as tif file
	Image.fromarray(img.astype(np.uint8)).save(path[:-4]+'_multiclass.tif')
	# Image.fromarray(img.astype(np.uint8)*255/np.max(list(labelencoder.values()))).save(path[:-4]+'_multiclass_rgb.tif')
	
	# to save as grayscale tif, can be modified to be multicolor tif
	# stacked_img = np.stack((img,)*3, -1)
	# imsave(path[:-4]+'_multiclass_rgb.tif', stacked_img)
	return

if __name__ == '__main__':
	import sys
	app = QApplication(sys.argv)
	dialogue=QFileDialog()
	dialogue.setNameFilter("*.csv");
	dialogue.setDefaultSuffix('csv')
	dialogue.setFileMode(QFileDialog.ExistingFiles)
	dialogue.exec()
	path=dialogue.selectedFiles()
	[produce_mask(p) for p in path]