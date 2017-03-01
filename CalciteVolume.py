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


def setMyAttributes(filename):
	s = GetSaveWindowAttributes()
	s.outputToCurrentDirectory = 0
	s.outputDirectory = "/Users/ushizima/Documents/ALS/text/sc2011/rock2"
	s.format = s.BMP
	s.fileName = filename
	s.width, s.height = 1920,1080#600,450 #1024,768
	s.resConstraint=s.NoConstraint
	s.stereo = 1
	s.screenCapture = 0
	SetSaveWindowAttributes(s)


setMyAttributes("part_e")	
Act_rotation_of_solid(True,180,720)

