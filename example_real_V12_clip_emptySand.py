########################################################################################
#Sample of idea
#Code for illustrating segmentation on solids imaged using synchroton x-ray micro-CT
#def main():
#	Initialization()
#	Act_slice_through()
#	Act_raw_data_appears_disappears()
#	Act_seg_data_appears()
#	Act_rotation_of_solid()
#Created: Sep 16th 2011
#Daniela Ushizima
#Acknowlegments:
#Rotation ----------- Gunther Weber
#Legends and axis --- Oliver Ruebel
########################################################################################

#0.Initialize parameters
global saveNow, nslices, maxYslices, step, step_transparency, rangeRotation, angle, myOutput, segData, rawData, slab


saveNow = True#False #save images to myOutput?
remote = True#False
slab = False
machine = 1

maxXslices = 1290#129
maxYslices = 1305#131#1305

nslices = 499
step = 20 #slicing step in x,y   # modified on v9

step_transparency = 10#1
#rangeRotation = 720# full is 720  #test=16
angle=0

#if new version, then ResampleAttributes, else ResamplePluginAttrib...@@@@@@@@
if (remote):
	myOutput = "C:\\dani\\Visualization\\SuperComputing\\2011\\test2"
  #"/home/ushizima/Documents/prog/Visit/SC2011/output/v2"
  #"/Users/ushizima/Documents/ALS/text/sc2011/rock1"
#"C:\\dani\\Visualization\\SuperComputing\\2011\\test2"
#
	if(machine==1):
		segData = "tesla.nersc.gov://global/scratch/sd/ushizima/als/sc2011/rock1/seg/seg.imgvol"
		rawData = "tesla.nersc.gov://global/scratch/sd/ushizima/als/sc2011/rock1/orig/orig.imgvol"
	elif(machine == 2):
		segData = "hopper.nersc.gov://global/scratch/sd/ushizima/als/sc2011/rock1/seg/seg.imgvol"
		rawData = "hopper.nersc.gov://global/scratch/sd/ushizima/als/sc2011/rock1/orig/orig.imgvol"
	elif(machine == 3):
		segData = "franklin.nersc.gov://scratch/scratchdirs/ushizima/efrc/als/sc2011/rock1/seg/seg.imgvol"
		rawData = "franklin.nersc.gov://scratch/scratchdirs/ushizima/efrc/als/sc2011/rock1/orig/orig.imgvol"
else:
	myOutput = "/home/ushizima/Documents/prog/Visit/SC2011/output/v2/"
	segData = "localhost:/home/ushizima/Documents/prog/Visit/SC2011/real_data/seg/segTest.imgvol"
	rawData = "localhost:/home/ushizima/Documents/prog/Visit/SC2011/real_data/orig/origTest.imgvol"

#Initialize plot----------------------------------------------------------------------------------
def setMyAttributes(filename):
	s = GetSaveWindowAttributes()
	s.outputToCurrentDirectory = 0
	s.outputDirectory = myOutput
	s.format = s.BMP
	s.fileName = filename
	s.width, s.height = 1920,1080#600,450 #1024,768
	s.resConstraint=s.NoConstraint
	s.stereo = 1
	s.screenCapture = 0
	SetSaveWindowAttributes(s)

def Initialization():
	InvertBackgroundColor()

	# Begin setting annotation of the graph - 
	Annot = GetAnnotationAttributes()	   #Get the current settings
	Annot.axes2D.visible = 0                  #Disable the axes in 2D
	Annot.axes3D.visible = 0                  #Disable the axes in 3D
	Annot.axes3D.bboxFlag = 1             #Disable the bounding box
	Annot.userInfoFlag = 0                      #Disable user information
	Annot.legendInfoFlag = 0                  #Disable all plot legends
	Annot.axes3D.triadFlag = 0             #Disable the triad in 3D
	Annot.databaseInfoFlag = 0             #Disable the database information
	Annot.foregroundColor = (255,255,255,255)
	Annot.backgroundColor = (0, 0, 0, 255)
	Annot.gradientBackgroundStyle = Annot.TopToBottom
	Annot.gradientColor1 = (255,255,255,255)
	Annot.backgroundMode = Annot.Solid#Annot.Gradient
	SetAnnotationAttributes(Annot)       #Set the new settings
	# End setting annotation

	#Set view
	from math import sin, cos, sqrt
	a = GetView3D()
	h = 0.5
	radian = float(-.5*angle+270) * (2. * 3.14159 / 360.)
	x = cos(radian)
	y = sin(radian)
	z = h
	l = sqrt(x*x + y*y + z*z)
	x = x / l
	y = y / l
	z = z / l
	a.viewNormal = (x, y, z)
	ux = -h*h*cos(radian)
	uy = -h*h*sin(radian)
	uz = h*h
	l = sqrt(ux*ux + uy*uy + uz*uz)
	ux = ux / l
	uy = uy / l
	uz = uz / l
	a.viewUp = (ux, uy, uz)
	#a.imageZoom = 1.5
	#a.nearPlane = -926.
	#a.farPlane = 926.
	SetView3D(a)

def Initialize_Pseudo(activePlot,pa,minT,maxT,colorTable,centering): #A.Segmented images	
	SetActivePlots(activePlot)
	AddPlot("Pseudocolor", "intensity")
	pa.legendFlag = 1
	pa.lightingFlag = 1
	pa.minFlag = 1
	pa.maxFlag = 1
	pa.opacity = 0
	pa.min = minT
	pa.max = maxT
	pa.pointSize = 0.05
	pa.pointType = pa.Point  # Box, Axis, Icosahedron, Point, Sphere
	pa.skewFactor = 1
	pa.opacity = 1
	pa.colorTableName = colorTable
	if(centering == "nodal"):
		pa.centering = pa.Nodal
	else:
		pa.centering = pa.Natural
	pa.smoothingLevel = 1
	pa.pointSizeVarEnabled = 0
	pa.pointSizeVar = "default"
	pa.pointSizePixels = 2
	SetPlotOptions(pa)
	SetActivePlots(activePlot)
	AddOperator("Threshold")	
	ThresholdAtts = ThresholdAttributes()
	ThresholdAtts.outputMeshType = 0
	ThresholdAtts.listedVarNames = ("default")
	ThresholdAtts.zonePortions = (1)
	ThresholdAtts.lowerBounds = (minT)
	ThresholdAtts.upperBounds = (maxT)
	ThresholdAtts.defaultVarName = "intensity"
	ThresholdAtts.defaultVarIsScalar = 1
	SetOperatorOptions(ThresholdAtts, 1)
	if (slab):
		applySlab(activePlot,pa)


def applySlab(activePlot,pa):
	slabSize = 300
	maxXslices = slabSize
	maxYslices = slabSize
	nslices = 10

	AddOperator("Resample")
	ra = ResamplePluginAttributes()#ResampleAttributes()
	ra.useExtents = 0
	ra.startX = 500
	ra.endX = ra.startX + slabSize
	ra.samplesX = slabSize
	ra.startY = 500
	ra.endY = ra.startY + slabSize
	ra.samplesY = slabSize
	ra.is3D = 1
	ra.startZ = 0
	ra.endZ = nslices
	ra.samplesZ = nslices
	ra.tieResolver = ra.random  # random, largest, smallest
	ra.tieResolverVariable = "default"
	ra.defaultValue = 0
	ra.distributedResample = 1
	SetOperatorOptions(ra, 0)
	

def Initialize_Volume_RawData(activePlot,va,minT,maxT):
	OpenDatabase(rawData, 0)	
	SetActivePlots(activePlot)	
	AddPlot("Volume", "intensity", 1, 0)	
	va.legendFlag = 1
	va.lightingFlag = 1
	va.colorControlPoints.GetControlPoints(0).colors = (0, 0, 255, 0)
	va.colorControlPoints.GetControlPoints(0).position = 0.339578
	va.colorControlPoints.GetControlPoints(1).colors = (0, 255, 255, 0)
	va.colorControlPoints.GetControlPoints(1).position = 0.470726
	va.colorControlPoints.GetControlPoints(2).colors = (0, 255, 0, 0)
	va.colorControlPoints.GetControlPoints(2).position = 0.548009
	va.colorControlPoints.GetControlPoints(3).colors = (255, 255, 0, 0)
	va.colorControlPoints.GetControlPoints(3).position = 0.629977
	va.colorControlPoints.GetControlPoints(4).colors = (255, 0, 0, 0)
	va.colorControlPoints.GetControlPoints(4).position = 0.784543
	va.colorControlPoints.smoothingFlag = 1
	va.colorControlPoints.equalSpacingFlag = 0
	va.colorControlPoints.discreteFlag = 0
	va.colorControlPoints.externalFlag = 0
	va.opacityAttenuation = 1

	#controlPoints does not contain any GaussianControlPoint objects.
	va.resampleTarget = 50000
	va.opacityVariable = "default"
	va.freeformOpacity = (2, 2, 2, 4, 4, 8, 9, 9, 9, 9, 11, 11, 15, 16, 16, 16, 16, 18, 18, 22, 23, 24, 24, 24, 24, 26, 26, 30, 31, 31, 31, 31, 33, 33, 37, 38, 38, 38, 38, 40, 40, 44, 45, 45, 45, 45, 46, 48, 48, 52, 53, 53, 53, 53, 55, 55, 59, 60, 60, 60, 60, 62, 62, 66, 67, 67, 67, 67, 70, 70, 70, 74, 75, 75, 75, 75, 77, 77, 81, 82, 82, 82, 82, 83, 83, 88, 88, 88, 88, 88, 90, 90, 92, 96, 97, 97, 97, 97, 98, 98, 103, 104, 104, 104, 104, 105, 105, 110, 110, 110, 110, 110, 112, 112, 117, 118, 119, 119, 119, 119, 120, 120, 125, 125, 125, 125, 125, 127, 127, 132, 132, 132, 132, 132, 134, 134, 139, 140, 140, 140, 140, 140, 142, 142, 147, 147, 147, 147, 147, 149, 149, 154, 154, 154, 154, 154, 156, 156, 161, 162, 162, 162, 162, 162, 164, 164, 169, 169, 169, 169, 169, 171, 171, 176, 176, 176, 176, 176, 178, 178, 182, 183, 183, 183, 183, 184, 186, 186, 191, 191, 191, 191, 191, 193, 193, 197, 198, 198, 198, 198, 200, 200, 204, 205, 205, 205, 205, 207, 207, 208, 213, 213, 213, 213, 213, 215, 215, 219, 220, 220, 220, 220, 222, 222, 226, 227, 227, 227, 227, 229, 229, 233, 234, 235, 235, 235, 235, 237, 237, 241, 242, 242, 242, 242, 244, 244, 248, 249, 249, 249, 249, 251, 251, 254, 254, 254)
	va.useColorVarMin = 1
	va.colorVarMin = minT
	va.useColorVarMax = 1
	va.colorVarMax = maxT
	va.useOpacityVarMin = 0
	va.opacityVarMin = 0
	va.useOpacityVarMax = 0
	va.opacityVarMax = 0
	va.smoothData = 0
	va.samplesPerRay = 500
	va.rendererType = va.RayCasting #va.Splatting  # Splatting, Texture3D, RayCasting, RayCastingIntegration, SLIVR
	va.gradientType = va.SobelOperator  # CenteredDifferences, SobelOperator
	va.num3DSlices = 200
	va.scaling = va.Linear  # Linear, Log10, Skew
	va.skewFactor = 1
	va.sampling = va.Rasterization  # KernelBased, Rasterization
	va.rendererSamples = 3
	SetPlotOptions(va)
	AddOperator("Threshold")
	ThresholdAtts = ThresholdAttributes()
	ThresholdAtts.outputMeshType = 0
	ThresholdAtts.listedVarNames = ("default")
	ThresholdAtts.zonePortions = (1)
	ThresholdAtts.lowerBounds = (minT)
	ThresholdAtts.upperBounds = (maxT)
	ThresholdAtts.defaultVarName = "intensity"
	ThresholdAtts.defaultVarIsScalar = 1
	SetOperatorOptions(ThresholdAtts, 1)
	#DrawPlots()


#3. Animations----------------------------------------------------------------------------------
def Act_slice_through(activePlot,pa_raw): #ACT 1

	#A. Prepare for slicing
	SetActivePlots(activePlot)#inner part
	AddOperator("Resample")
	ra = ResampleAttributes()
	#Cutting plane through Z
	for z in range(1,nslices,10):
		ra.useExtents = 0
		ra.startX = 0
		ra.endX = maxXslices
		ra.samplesX = maxXslices
		ra.startY = 0
		ra.endY = maxYslices
		ra.samplesY = maxYslices
		ra.is3D = 1
		ra.startZ = 0
		ra.endZ = z
		ra.samplesZ = z
		ra.tieResolver = ra.random  # random, largest, smallest
		ra.tieResolverVariable = "default"
		ra.defaultValue = 0
		ra.distributedResample = 1
		SetOperatorOptions(ra, 0)
		DrawPlots()
	  	if (saveNow): SaveWindow()
	for z in range(nslices,1,-20):
		ra.useExtents = 0
		ra.startX = 0
		ra.endX = maxXslices
		ra.samplesX = maxXslices
		ra.startY = 0
		ra.endY = maxYslices
		ra.samplesY = maxYslices
		ra.is3D = 1
		ra.startZ = 0
		ra.endZ = z
		ra.samplesZ = z
		ra.tieResolver = ra.random  # random, largest, smallest
		ra.tieResolverVariable = "default"
		ra.defaultValue = 0
		ra.distributedResample = 1
		SetOperatorOptions(ra, 0)
		DrawPlots()
	  	if (saveNow): SaveWindow()
	RemoveOperator(1, 0)

	#Cutting plane through Y
	AddOperator("ThreeSlice")	
	ThreeSliceAtts = ThreeSliceAttributes()	
	for y in range(0,(maxXslices-1),step): 
	  ThreeSliceAtts.x = y
	  ThreeSliceAtts.y = y
	  ThreeSliceAtts.z = 1
	  ThreeSliceAtts.interactive = 1
	  SetOperatorOptions(ThreeSliceAtts, 1)
	  if (y<90):
		Act_rotation_of_solid(True,y,(y+1)) #rotation only until reaching good view
	  else:
		if(y==90): 		
			a = GetView3D()
			a.imageZoom = 1.15
			#step = 10
		DrawPlots()
		if (saveNow): SaveWindow()

def Act_decrease_opacity(activePlot,activeObj):
	SetActivePlots(activePlot)#outer part
	for op in range(100,0,-step_transparency):
          activeObj.opacity = float(op)/float(100)
          SetPlotOptions(activeObj)
	  DrawPlots()
	  if (saveNow): SaveWindow()
	DeleteActivePlots()


def Act_increase_opacity_object(activePlot,activeObj): #ACT 2
	for op in range(0,100,step_transparency):
 	  SetActivePlots(activePlot)#outer part
	  activeObj.opacityAttenuation = float(op)/float(100)
	  SetPlotOptions(activeObj)
	  DrawPlots()


def Act_rotation_of_solid(slow,iRangeRotation,eRangeRotation): #ACT 1
	from math import sin, cos, sqrt
	if (slow): 
		rangeRot = range(iRangeRotation,eRangeRotation,10)
	else:
		rangeRot = range(iRangeRotation,eRangeRotation,20)
	a = GetView3D()
	for angle in rangeRot:
	  h = 0.5
	  radian = float(-.5*angle+270) * (2. * 3.14159 / 360.)
	  x = cos(radian)
	  y = sin(radian)
	  z = h
	  l = sqrt(x*x + y*y + z*z)
	  x = x / l
	  y = y / l
	  z = z / l
	  a.viewNormal = (x, y, z)
	  ux = -h*h*cos(radian)
	  uy = -h*h*sin(radian)
	  uz = h*h
	  l = sqrt(ux*ux + uy*uy + uz*uz)
	  ux = ux / l
	  uy = uy / l
	  uz = uz / l
	  a.viewUp = (ux, uy, uz)
	  #a.nearPlane = -40.
	  #a.farPlane = 40.
	  SetView3D(a)
	  DrawPlots()
	  if (saveNow): SaveWindow()

def Act_rotation_of_solid_clockwise(slow,eRangeRotation,iRangeRotation): #ACT 1
	from math import sin, cos, sqrt
	if (slow): 
		rangeRot = range(eRangeRotation,iRangeRotation,-10)
	else:
		rangeRot = range(eRangeRotation,iRangeRotation,-20)
	a = GetView3D()
	for angle in rangeRot:
	  h = 0.5
	  radian = float(-.5*angle+270) * (2. * 3.14159 / 360.)
	  x = cos(radian)
	  y = sin(radian)
	  z = h
	  l = sqrt(x*x + y*y + z*z)
	  x = x / l
	  y = y / l
	  z = z / l
	  a.viewNormal = (x, y, z)
	  ux = -h*h*cos(radian)
	  uy = -h*h*sin(radian)
	  uz = h*h
	  l = sqrt(ux*ux + uy*uy + uz*uz)
	  ux = ux / l
	  uy = uy / l
	  uz = uz / l
	  a.viewUp = (ux, uy, uz)
	  #a.nearPlane = -40.
	  #a.farPlane = 40.
	  SetView3D(a)
	  DrawPlots()
	  if (saveNow): SaveWindow()

def Act_obj1_fade_obj2_showUp(object1,object1_is_volume,object2,maxOpacObject2): #ACT 3	
	#Inner part comes in and outer part fades away
	for op in range(100,0,-step_transparency):
 	  SetActivePlots(0)#outer part
	  if (object1_is_volume):#object1 is volume	
	  	object1.opacityAttenuation = float(op)/float(100)
	  else:
	  	object1.opacity = float(op)/float(100)
	  SetPlotOptions(object1)
	  SetActivePlots(1)#inner part
	  if((1. - (float(op)/float(100))) < maxOpacObject2):	  
	  	object2.opacity = 1. - (float(op)/float(100))
	  SetPlotOptions(object2)
	  DrawPlots()
	  if (saveNow): SaveWindow()
	SetActivePlots(0)#outer part
	DeleteActivePlots()

def Act_slicing_segmentation(pa_seg):
	AddOperator("Clip")
	DemoteOperator(1,1)
	j = 0
	for i in range(1,10):
		ClipAtts = ClipAttributes()
		ClipAtts.quality = ClipAtts.Fast  # Fast, Accurate
		ClipAtts.funcType = ClipAtts.Sphere  # Plane, Sphere
		ClipAtts.plane1Status = 1
		ClipAtts.plane2Status = 0
		ClipAtts.plane3Status = 0
		ClipAtts.plane1Origin = (0, 0, 0)
		ClipAtts.plane2Origin = (0, 0, 0)
		ClipAtts.plane3Origin = (0, 0, 0)
		ClipAtts.plane1Normal = (1, 0, 0)
		ClipAtts.plane2Normal = (0, 1, 0)
		ClipAtts.plane3Normal = (0, 0, 1)
		ClipAtts.planeInverse = 0
		ClipAtts.planeToolControlledClipPlane = ClipAtts.Plane1  # None, Plane1, Plane2, Plane3
		ClipAtts.center = (200+i*10, 200, 180)
		ClipAtts.radius = 400
		ClipAtts.sphereInverse = 0
		SetOperatorOptions(ClipAtts, 1)
		DrawPlots()
		if (saveNow): SaveWindow()


def Act_zoom_in_out():
	end_range = 10#40
	for zoom in range(1,end_range,1):
		v = GetView3D()
		v.imageZoom = v.imageZoom + ( float(zoom)/100.0)
		SetView3D(v)
		DrawPlots()
		if (saveNow): SaveWindow()
	for zoom in range(end_range,1,-1):
		v = GetView3D()
		v.imageZoom = v.imageZoom - ( float(zoom)/100.0)
		SetView3D(v)
		DrawPlots()
		if (saveNow): SaveWindow()

def Act_isovolume(activePlot):
	#RemoveAllOperators()
	DefineScalarExpression("suave", "median_filter(intensity)")
	DefineScalarExpression("binary_seg", "if(ge(suave,70),255,0 )" ) #minT = 70
	ChangeActivePlotsVar("binary_seg")
	ThresholdAtts = ThresholdAttributes()
	ThresholdAtts.outputMeshType = 0
	ThresholdAtts.listedVarNames = ("default")
	ThresholdAtts.zonePortions = (1)
	ThresholdAtts.lowerBounds = 254
	ThresholdAtts.upperBounds = 255
	ThresholdAtts.defaultVarName = "intensity"
	ThresholdAtts.defaultVarIsScalar = 1
	SetOperatorOptions(ThresholdAtts, 1)

	SetActivePlots(activePlot)#outer part
	AddOperator("Isovolume", 0)
	PromoteOperator(0)
	IsovolumeAtts = IsovolumeAttributes()
	#IsovolumeAtts.lbound = 200
	#IsovolumeAtts.ubound = 255
	IsovolumeAtts.variable = "default"
	SetOperatorOptions(IsovolumeAtts, 0)
	a = GetView3D()
	a.nearPlane = -900.048642254
	a.farPlane = 900.048642254
	SetView3D(a)


def main():	
	RemoveAllOperators()
	Initialization()                                         
	#ACT 1 - slicing through raw data gray levels
	setMyAttributes("part_a")
	pa_raw = PseudocolorAttributes()
	OpenDatabase(rawData)
	Initialize_Pseudo(0,pa_raw,50,200,"xray","natural") #show raw data in xray colors
	Act_slice_through(0,pa_raw) #using rotation of 0-90

	#ACT 2 - slicing through raw data gray levels
	setMyAttributes("part_b")
	pa_raw2 = PseudocolorAttributes()
	Initialize_Pseudo(0,pa_raw2,60,170,"rainbow","nodal") #show raw data in xray colors
	maxOpacObject2 = 0.7
	Act_obj1_fade_obj2_showUp(pa_raw,False,pa_raw2,maxOpacObject2)
	Act_rotation_of_solid(True,90,180) #rotating the raw data volume = fast==false

	#Act 3 - come orange segmentation and slicing
	setMyAttributes("part_c")
	pa_seg = PseudocolorAttributes()
	OpenDatabase(segData)
	minT=70
	maxT=140
	Initialize_Pseudo(1,pa_seg,minT,maxT,"orangehot","natural") #segdata
	maxOpacObject2 = 0.55	
	Act_obj1_fade_obj2_showUp(pa_raw2,False,pa_seg,maxOpacObject2)       	
	SetPlotOptions(pa_seg)
	CloseDatabase(rawData)
	Act_rotation_of_solid_clockwise(True,180,90)
	Act_slicing_segmentation(pa_seg)


	#Act 4 - come segmentation with plain red color
	setMyAttributes("part_d")
	pa_seg2 = PseudocolorAttributes()
	Initialize_Pseudo(1,pa_seg2,minT,maxT,"rainbow","nodal") #segdata
	Act_obj1_fade_obj2_showUp(pa_seg,False,pa_seg2,0.7) #object1_is_volume = false
	Act_rotation_of_solid(False,90,180) #(fast, rangeRotation)
	pa_seg2.opacity = 0.6
	SetPlotOptions(pa_seg2)
	Act_zoom_in_out()
	Act_rotation_of_solid(False,180,720) #(fast, rangeRotation)
	CloseDatabase(segData)

main()
#Exit()
