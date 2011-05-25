import sys
import time
import random
import copy
import Image

INPUT_SIZE = 3
NODES_NUMOF = 8
LEARNING_RATE = 0.05
PASSES_NUMOF = 5
DEFAULT_IMAGE_NAME = "image.bmp"
# AVG_DECAY_PERIOD = imsize # Assigned below

#Identify the winning node
def find_winner_bsom():
	maxprob = 0.0
	maxz = -1
	for z in range(NODES_NUMOF):
		p2 = p2s[z]
		p1 = 1.0
		p3 = 1.0
		for i in range(INPUT_SIZE):
			p1 *= (1.0-abs(bsom[z][i]-xs[i]))
			p3 *= (1.0-abs(inputavgs[i]-xs[i]))

		prob = p1/p3
		#prob = (p1*p2)/p3
		#if x%100 == 10:
		#	print "node",z,"p1",p1,"p2",p2,"p3",p3,"prob",prob

		if prob > maxprob:
			maxprob = prob
			maxz = z

	#print "pixel",rgb
	#if x%50 == 10:
	#	print "input",xs
	#	print "maxprob",maxprob,"winz",maxz
	#	print "Winner",maxz,"prob",maxprob
	return maxz

def find_winner_som():
	mindiff = 1.0*INPUT_SIZE
	minz = -1
	for z in range(NODES_NUMOF):
		diff = 0.0
		for i in range(INPUT_SIZE):
			diff += abs(som[z][i]-xs[i])
		if diff < mindiff:
			mindiff = diff
			minz = z
	return minz

def find_winner_kmeans():
	mindiff = 1.0*INPUT_SIZE
	minz = -1
	for z in range(NODES_NUMOF):
		diff = 0.0
		for i in range(INPUT_SIZE):
			diff += abs(kmeans[z][i]-xs[i])
		if diff < mindiff:
			mindiff = diff
			minz = z
	return minz

def calc_p2s():
	connectwins = [0 for i in range(NODES_NUMOF)]
	for y in range(im.size[1]):
		for x in range(im.size[0]):
			# Get input
			rgb2=im.getpixel((x,y))
			xs2=[0.0,0.0,0.0]
			for c in range(INPUT_SIZE):
				xs2[c]=rgb2[c]/255.0

			mindiff = 1.0*INPUT_SIZE
			minz = -1
			for z in range(NODES_NUMOF):
				diff = 0.0
				for i in range(INPUT_SIZE):
					diff += abs(bsom[z][i]-xs2[i])
				if diff < mindiff:
					mindiff = diff
					minz = z
	
			connectwins[minz] += 1

	for n in range(NODES_NUMOF):
		p2s[n]=float(connectwins[n])/float(imsize)
	#print "P2s",p2s

# Open image
if len(sys.argv) > 1:
	image_name = sys.argv[1]
else:
	image_name = DEFAULT_IMAGE_NAME
im = Image.open(image_name)
im.show()
bsomim = Image.open(image_name)
bsomg = Image.new("RGB",(NODES_NUMOF,1))
somim = Image.open(image_name)
kmeansim = Image.open(image_name)
imsize = im.size[0]*im.size[1]
AVG_DECAY_PERIOD = imsize
print "Image",image_name,"height",im.size[0],"width",im.size[1],"size",imsize

# Calculate global averages
inputavgs = [0.0 for i in range(INPUT_SIZE)]
for y in range(im.size[1]):
	for x in range(im.size[0]):
		rgb=im.getpixel((x,y))
		xs=[0.0,0.0,0.0]
		for c in range(INPUT_SIZE):
			xs[c]=rgb[c]/255.0
			inputavgs[c] += xs[c] 
for c in range(INPUT_SIZE):
	inputavgs[c] /= float(imsize)
print "RGB avgs",inputavgs

# BSOM initialisation
print "input size",INPUT_SIZE,"number of nodes", NODES_NUMOF
print "learning rate",LEARNING_RATE,"number of passes",PASSES_NUMOF
bsom = [[random.uniform(0.0,1.0) for i in range(INPUT_SIZE)] for j in range(NODES_NUMOF)]
p2s = [0.0 for i in range(NODES_NUMOF)]
#calc_p2s()
		
# SOM initialisation
som = copy.deepcopy(bsom)
somupdatecounts = [0 for i in range(NODES_NUMOF)]

# k means initialisation
kmeans = []
for r in range(NODES_NUMOF):
	h = random.randint(0,im.size[0]-1)
	w = random.randint(0,im.size[1]-1)
	rgb=im.getpixel((h,w))
	#print "h,w",h,w
	#print "rgb",rgb[0],rgb[1],rgb[2] 
	mean=[0.0,0.0,0.0]
	for c in range(INPUT_SIZE):
		mean[c]=rgb[c]/255.0
	kmeans.append(mean)

# Learning loop
print "BSOM",bsom
print "SOM",som
print "k-means",kmeans
lastupdatessum = 0.0
for passnum in range(PASSES_NUMOF):
	print "Pass",passnum
	#print "P2s",p2s
	bsomupdatecounts = [0 for i in range(NODES_NUMOF)]
	bsomupdatessum = 0.0
	somupdatessum = 0.0
	kmeansupdatessum = 0.0
	for y in range(im.size[1]):
	#for y in range(2):
		for x in range(im.size[0]):
		#for x in range(2):

			# Get input
			rgb=im.getpixel((x,y))
			xs=[0.0,0.0,0.0]
			for c in range(INPUT_SIZE):
				xs[c]=rgb[c]/255.0

			# Update winner weights
			winz = find_winner_bsom()
			for i in range(INPUT_SIZE):
				bsomupdatessum+=abs((xs[i]-bsom[winz][i])*LEARNING_RATE)
				bsom[winz][i]+=(xs[i]-bsom[winz][i])*LEARNING_RATE
				bsomupdatessum+=abs((xs[i]-bsom[(winz-1)%NODES_NUMOF][i])*LEARNING_RATE*LEARNING_RATE)
				bsom[(winz-1)%NODES_NUMOF][i]+=(xs[i]-bsom[(winz-1)%NODES_NUMOF][i])*LEARNING_RATE*LEARNING_RATE
				bsomupdatessum+=abs((xs[i]-bsom[(winz+1)%NODES_NUMOF][i])*LEARNING_RATE*LEARNING_RATE)
				bsom[(winz+1)%NODES_NUMOF][i]+=(xs[i]-bsom[(winz+1)%NODES_NUMOF][i])*LEARNING_RATE*LEARNING_RATE
			#if x%100 == 0:
			#	print "New weights ",som[winz]
			bsomupdatecounts[winz]+=1

			winz = find_winner_som()
			for i in range(INPUT_SIZE):
				somupdatessum+=abs((xs[i]-som[winz][i])*LEARNING_RATE)
				som[winz][i]+=(xs[i]-som[winz][i])*LEARNING_RATE
				somupdatessum+=abs((xs[i]-som[(winz-1)%NODES_NUMOF][i])*LEARNING_RATE*LEARNING_RATE)
				som[(winz-1)%NODES_NUMOF][i]+=(xs[i]-som[(winz-1)%NODES_NUMOF][i])*LEARNING_RATE*LEARNING_RATE
				somupdatessum+=abs((xs[i]-som[(winz+1)%NODES_NUMOF][i])*LEARNING_RATE*LEARNING_RATE)
				som[(winz+1)%NODES_NUMOF][i]+=(xs[i]-som[(winz+1)%NODES_NUMOF][i])*LEARNING_RATE*LEARNING_RATE
	
			winz = find_winner_kmeans()
			for i in range(INPUT_SIZE):
				kmeansupdatessum+=abs((xs[i]-kmeans[winz][i])*LEARNING_RATE)
				kmeans[winz][i]+=(xs[i]-kmeans[winz][i])*LEARNING_RATE
	#calc_p2s()
	#for i in range(NODES_NUMOF):
	#	print (int(som[i][0]*255.0),int(som[i][1]*255.0),int(som[i][2]*255.0))
	print "Sum BSOM updates this round",bsomupdatessum
	print "Sum SOM updates this round",somupdatessum
	print "Sum k-means updates this round",kmeansupdatessum
	#print "Change in sum BSOM updates",bsomupdatessum-lastupdatessum
	#lastupdatessum = updatessum
	#lastbsomupdatecounts = bsomupdatecounts
	#for z in range(NODES_NUMOF):
	#	updateavgs[z] = float(lastbsomupdatecounts[z])/float(imsize)

	# Recolour image		
	bsomerr = 0.0
	somerr = 0.0
	kmeanserr = 0.0
	for y in range(im.size[1]):
		for x in range(im.size[0]):

			# Get input
			rgb=im.getpixel((x,y))
			xs=[0.0,0.0,0.0]
			for c in range(INPUT_SIZE):
				xs[c]=rgb[c]/255.0
			#print "RGB",rgb," xs",xs

			# Recolour pixel to winner colour
			winz = find_winner_bsom()
			for c in range(INPUT_SIZE):
				bsomerr += abs(bsom[winz][c]-xs[c])
			bsomim.putpixel((x,y),(int(bsom[winz][0]*255.0),int(bsom[winz][1]*255.0),int(bsom[winz][2]*255.0)))

			winz = find_winner_som()
			for c in range(INPUT_SIZE):
				somerr += abs(som[winz][c]-xs[c])
			somim.putpixel((x,y),(int(som[winz][0]*255.0),int(som[winz][1]*255.0),int(som[winz][2]*255.0)))

			winz = find_winner_kmeans()
			for c in range(INPUT_SIZE):
				kmeanserr += abs(kmeans[winz][c]-xs[c])
			kmeansim.putpixel((x,y),(int(kmeans[winz][0]*255.0),int(kmeans[winz][1]*255.0),int(kmeans[winz][2]*255.0)))

	print "BSOM error",bsomerr
	print "SOM error",somerr
	print "k-means error",kmeanserr

somim.show()
time.sleep(1)
kmeansim.show()
time.sleep(1)
bsomim.show()
#print "P2s",p2s
#print "BSOM updates",bsomupdatecounts
#print "SOM updates",somupdatecounts
print "BSOM",bsom
print "SOM",som
print "k-means",kmeans

