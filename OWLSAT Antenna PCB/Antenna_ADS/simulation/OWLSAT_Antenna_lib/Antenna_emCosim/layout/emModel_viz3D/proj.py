# Automatically generated file proj.py"

# Generated with $Id: extrusion_to_empro.cpp 11193 2012-11-22 13:42:22Z mdewilde $ 

import empro, empro.toolkit

def getVersion():
	return 11

def getSessionVersion(session):
	try:
		return session.getVersion()
	except AttributeError:
		return 0

def get_ads_import_version():
	try:
		ads_import_version = empro.toolkit.ads_import.getVersion()
	except AttributeError:
		ads_import_version = 0
	return ads_import_version

def ads_simulation_settings():
	set_frequency_plan_and_common_options()
	set_FEM_options()

def set_frequency_plan_and_common_options():
	try:
		sim=empro.activeProject.simulationSettings
	except AttributeError:
		sim=empro.activeProject.createSimulationData()
	# Frequency plan:
	frequency_plan_list=sim.femFrequencyPlanList()
	frequency_plan=empro.simulation.FrequencyPlan()
	frequency_plan.type="Adaptive"
	frequency_plan.startFrequency=0
	frequency_plan.stopFrequency=500000000
	frequency_plan.samplePointsLimit=50
	frequency_plan_list.append(frequency_plan)
	if 'minFreq' in empro.activeProject.parameters:
		empro.activeProject.parameters.setFormula('minFreq','0 GHz')
	if 'maxFreq' in empro.activeProject.parameters:
		empro.activeProject.parameters.setFormula('maxFreq','0.5 GHz')
	sim.saveFieldsFor="AllFrequencies"

def set_FEM_options():
	# Simulation options:
	try:
		sim=empro.activeProject.simulationSettings
	except AttributeError:
		sim=empro.activeProject.createSimulationData()
	sim.simulator = "com.keysight.xxpro.simulator.fem"
	try:
		sim.ambientConditions.backgroundTemperature = "25 degC"
	except AttributeError:
		pass
	try:
		sim.femEigenMode = False
	except AttributeError:
		pass
	try:
		sim.portOnlyMode = False
	except AttributeError:
		pass
	try:
		sim.transfinitePorts  = False
	except AttributeError:
		pass
	sim.femMeshSettings.minimumNumberOfPasses      = 2
	sim.femMeshSettings.maximumNumberOfPasses      = 15
	sim.femMeshSettings.deltaError                 = 0.02
	sim.femMeshSettings.refineAtSpecificFrequency  = False
	sim.femMeshSettings.refinementFrequency        = "0 GHz"
	sim.femMeshSettings.requiredConsecutivePasses  = 1
	sim.femMeshSettings.meshRefinementPercentage   = 25
	sim.femMeshSettings.orderOfBasisFunctions      = 2
	try:
		sim.femMeshSettings.useMinMeshSize               = False
	except AttributeError:
		pass
	try:
		sim.femMeshSettings.minMeshSize                  = "0 m" 
	except AttributeError:
		pass
	try:
		sim.femMeshSettings.autoTargetMeshSize           = True
		sim.femMeshSettings.useTargetMeshSize            = True
	except AttributeError:
		pass
	try:
		sim.femMeshSettings.targetMeshSize               = "0 m" 
	except AttributeError:
		pass
	try:
		sim.femMeshSettings.edgeMeshLength               = "0 m" 
	except AttributeError:
		pass
	try:
		sim.femMeshSettings.vertexMeshLength               = "0 m" 
	except AttributeError:
		pass
	try:
		sim.femMeshSettings.mergeObjectsOfSameMaterial = True
	except AttributeError:
		pass
	try:
		sim.femMeshSettings.alwaysSolveOnFinestMesh = False
	except AttributeError:
		pass
	try:
		sim.femMeshSettings.autoConductorMeshing = False
	except AttributeError:
		pass
	try:
		empro.activeProject.gridGenerator.femPadding.useDefault = False
	except AttributeError:
		pass
	try:
		sim.dataSetFileName                            = ''
	except AttributeError:
		pass
	try:
		sim.femMatrixSolver.solverType                    = "MatrixSolverAuto"
	except ValueError: # Old versions of EMPro (< 2017) do not have the auto-select solver option
		sim.femMatrixSolver.solverType                    = "MatrixSolverDirect"
	sim.femMatrixSolver.maximumNumberOfIterations     = 500
	sim.femMatrixSolver.tolerance                     = 1e-05
	try:
		sim.femMeshSettings.refinementStrategy="maxFrequency"
	except AttributeError:
		pass

def get_session(usedFlow="ADS"):
	ads_import_version = get_ads_import_version()
	if ads_import_version >= 3:
		session=empro.toolkit.ads_import.Import_session(units="um", wall_boundary="Radiation",usedFlow=usedFlow,adsProjVersion=getVersion())
		return session
	try:
		session=empro.toolkit.ads_import.Import_session(units="um", wall_boundary="Radiation",usedFlow=usedFlow)
	except TypeError: # usedFlow may not be available in old FEM bits
		session=empro.toolkit.ads_import.Import_session(units="um", wall_boundary="Radiation")
	return session

def _dummyUpdateProgress(value):
	pass

def _createIfToggleExtensionToBoundingBoxExpression(exprTrue,exprFalse):
	if get_ads_import_version() >= 11:
		return "if(toggleExtensionToBoundingBox, %s, %s)" % (exprTrue, exprFalse)
	else:
		return exprFalse

def ads_import(usedFlow="ADS",topAssembly=None,session=None,demoMode=False,includeInvalidPorts=True,suppressNotification=False,updateProgressFunction=_dummyUpdateProgress,materialForEachLayer=False):
	ads_simulation_settings()
	importer = projImporter(usedFlow,session,updateProgressFunction)
	rv = importer.ads_import(usedFlow,topAssembly,demoMode,includeInvalidPorts,suppressNotification,materialForEachLayer)
	try:
		empro.activeProject.gridGenerator.femPadding.useDefault = False
	except AttributeError:
		pass
	return rv

class projImporter():
	def __init__(self,usedFlow="ADS",session=None,updateProgressFunction=_dummyUpdateProgress):
		self.usedFlow = usedFlow
		if session==None:
			self.session=get_session(usedFlow)
		else:
			self.session = session
		if getSessionVersion(self.session) >= 8:
			self.session.setProjImporter(self)
		self.roughnesses={}
		self.materials={}
		self.substratePartNameMap={}
		self.substrateLayers=[] # ordered list with substrate layers
		self.waveforms={}
		self.circuitComponentDefinitions={}
		self.initNetlists()
		self.updateProgressFunction = updateProgressFunction
		if updateProgressFunction == _dummyUpdateProgress:
			if getSessionVersion(self.session) >= 10:
				self.updateProgressFunction = self.session.getUpdateProgressFunction()
		self.geoProgress = 0

	def _updateProgress(self,progress):
		self.updateProgressFunction(progress)

	def _setModelTypeForMetals(self,material,value):
		if getSessionVersion(self.session) >= 2:
			self.session.setModelTypeForMetals(material,value)
			return
		try:
			material.details.electricProperties.parameters.useSurfaceConductivityCorrection = value
		except:
			pass
	def _checked_roughness(self,roughnessTypeString,*args):
		try:
			roughnessConstructor = getattr(empro.material,roughnessTypeString)
			return roughnessConstructor(*args)
		except AttributeError:
			print("Warning: unsupported surface roughness type %s. Roughness will be ignored." % roughnessTypeString)
			return None
	def _create_parameter(self,iParName,iFormula,iNotes,iUserEditable,fixGridAxis=""):
		if getSessionVersion(self.session) >= 2:
			self.session.create_parameter(iParName,iFormula,iNotes,iUserEditable,fixGridAxis)
			return
		try:
			self.session.create_parameter(iParName,iFormula,iNotes,iUserEditable)
		except AttributeError:
			empro.activeProject.parameters.append(iParName,iFormula,iNotes,iUserEditable)
		if fixGridAxis in ['X','Y','Z']:
			gG = empro.activeProject.gridGenerator
			newFP = empro.libpyempro.mesh.FixedPoint()
			if fixGridAxis == 'X':
				location = (iParName,0,0)
			elif fixGridAxis == 'Y':
				location = (0,iParName,0)
			elif fixGridAxis == 'Z':
				location = (0,0,iParName)
			newFP.location = location
			newFP.axes=fixGridAxis
			gG.addManualFixedPoint(newFP)
	def _circularGridRegion(self,x,y,radius):
		radius = empro.core.Expression(radius)
		newGRP = empro.libpyempro.mesh.ManualGridRegionParameters()
		newGRP.cellSizes.target = (radius,radius,0)
		newGRP.gridRegionDirections="X|Y"
		newGRP.regionBounds.lower = (x-radius,y-radius,0)
		newGRP.regionBounds.upper = (x+radius,y+radius,0)
		return newGRP
	def _partGridParameters(self,targetCellSize):
		targetCellSize = empro.core.Expression(targetCellSize)
		newGP = empro.libpyempro.mesh.PartGridParameters()
		newGP.cellSizes.target = (targetCellSize,targetCellSize,0)
		newGP.gridRegionDirections="X|Y"
		newGP.useGridRegions = True
		return newGP
	def _create_sketch(self,pointString,sketch=None,closed=True):
		if getSessionVersion(self.session) >= 4:
			return self.session.create_sketch(pointString,sketch,closed)
		V=empro.geometry.Vector3d
		L=empro.geometry.Line
		def stringToPoint(s):
			sList = s.split('#')
			return V(sList[0],sList[1],0)
		if sketch == None:
			sketch=empro.geometry.Sketch()
		pointList = [ stringToPoint(x) for x in pointString.split(';') ]
		if closed:
			edges = [ L(pointList[i-1],pointList[i]) for i in range(len(pointList)) ]
		else:
			edges = [ L(pointList[2*i],pointList[2*i+1]) for i in range(len(pointList)/2) ]
		sketch.addEdges(edges)
		return sketch
	def _create_extrude(self, pointStrings, height, up):
		if getSessionVersion(self.session) >= 14:
			return self.session.create_extrude(pointStrings, height, up)
		else:
			sketch = None
			for pointString in pointStrings:
				sketch = self._create_sketch(pointString, sketch)
			part = empro.geometry.Model()
			part.recipe.append(empro.geometry.Extrude(sketch, height, empro.geometry.Vector3d(0, 0, (-1, 1)[up])))
			return part
	def _create_cover(self, pointStrings):
		if getSessionVersion(self.session) >= 14:
			return self.session.create_cover(pointStrings)
		else:
			sketch = None
			for pointString in pointStrings:
				sketch = self._create_sketch(pointString, sketch)
			part = empro.geometry.Model()
			part.recipe.append(empro.geometry.Cover(sketch))
			return part
	def _create_bondwire(self,radius, segments, points, name=None,bwAssembly=None,topAssembly=None,material=None,partModifier=(lambda x : x),profile=None,above=True):
		if getSessionVersion(self.session) >= 13:
			part = self.session.create_bondwire(radius, segments, points, name, bwAssembly,topAssembly,material,partModifier,profile,above)
		else:
			if profile is not None:
				part = empro.geometry.Model()
				try:
					part.recipe.append(empro.geometry.Bondwire(points[0],points[-1],profile))
				except TypeError:
					# Only for compatibility with EMPro 2011.02 or older
					self.session.warnings.append('For importing bondwires with profile definitions it is advised to use EMPro 2012.09 or later.')
					bw=empro.geometry.Bondwire(points[0],points[-1],empro.geometry.BondwireDefinition(name,radius,segments))
					bw.definition=profile
					part.recipe.append(bw)
				if not above:
					import math
					part.coordinateSystem.rotate(math.pi,0,0)
				part = partModifier(part)
				bwAssembly.append(part)
				part.name = name
				empro.toolkit.applyMaterial(part,material)
			else:
				try:
					part = self.session.create_bondwire(radius, segments, points, name, bwAssembly,topAssembly,material,partModifier)
				except TypeError:
					part = self.session.create_bondwire(radius, segments, points)
					part = partModifier(part)
					bwAssembly.append(part)
					part.name = name
					empro.toolkit.applyMaterial(part,material)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=2000
		return part
	def _create_internal_port(self, name, definitionString, head, tail, extent=None):
		if getSessionVersion(self.session) < 15 and (isinstance(head, list) or isinstance(tail, list)):
			raise RuntimeError("Ports having multiple positive or negative pins are not yet supported")
		if getSessionVersion(self.session) >= 9:
			return self.session.create_internal_port(name, definitionString, head, tail, extent)
		port=empro.components.CircuitComponent()
		port.name=name
		port.definition=self.circuitComponentDefinitions[definitionString]
		port.head=head
		port.tail=tail
		if extent != None:
			port.extent=extent
			port.useExtent=True
		return port
	def _set_extra_port_info(self, port, termType, number, name, feedType, mode = -1):
		try:
			if get_ads_import_version() >= 17:
				self.session.set_extra_port_info(port=port, termType=termType, number=number, name=name, mode=mode, feedType=feedType)
			else:
				self.session.set_extra_port_info(port=port, termType=termType, number=number, name=name, mode=mode)
		except AttributeError:
			pass
		global g_portNbToName
		g_portNbToName[number] = (name, mode)
	def _setAssemblyMeshSettings(self,a,vertexMeshLength=0,edgeMeshLength=0,surfaceMeshLength=0):
		if vertexMeshLength==0 and edgeMeshLength==0 and surfaceMeshLength==0:
			return
		if getSessionVersion(self.session) >= 12:
			self.session.setAssemblyMeshSettings(a,vertexMeshLength,edgeMeshLength,surfaceMeshLength)
			return
		parts = [x for x in a.flatList(False)]
		for x in parts:
			x.meshParameters.vertexMeshLength=vertexMeshLength
			x.meshParameters.edgeMeshLength=edgeMeshLength
			x.meshParameters.surfaceMeshLength=surfaceMeshLength
	def _getEMProMaterialName(self,ADSmaterialName,ADSmaterialMap,extraMaterialProperties,ADSmaterialsNo1to1):
		EMProMaterialName=ADSmaterialName
		if ADSmaterialName in [x for (x,y) in ADSmaterialMap.keys()]:
			EMProMaterialName+="_"+str(extraMaterialProperties)
			if not ADSmaterialName in ADSmaterialsNo1to1:
				ADSmaterialsNo1to1.append(ADSmaterialName)
				self.session.warnings.append('The ADS material '+ADSmaterialName+' is used on masks with different precedence, sheet thickness or modeltype for metals and has therefore been mapped to multiple EMPro materials.')
		return EMProMaterialName
	def create_bondwire_definitions(self):
		self.bondwire_definitions={}
		if not hasattr(empro.activeProject,"bondwireDefinitions"):
			return
	def create_materials(self,materialForEachLayer=False):
		ADSmaterialMap={}
		EMProNameMaterialMap={}
		layerEMProMaterialNameMap={}
		ADSmaterialsNo1to1=[]
		ADSmaterialName=["AIR","simulation_box"][materialForEachLayer]
		extraMaterialProperties=(0,None,None,False) # (priority,thickness,modelTypeForMetals,convertedToResistance)
		material=ADSmaterialMap.get((ADSmaterialName,extraMaterialProperties),None)
		if material == None:
			EMProMaterialName = self._getEMProMaterialName(ADSmaterialName,ADSmaterialMap,extraMaterialProperties,ADSmaterialsNo1to1)
			material=self.session.create_material(name=EMProMaterialName, color=(255,255,255,0), permittivity=1, permeability=1)
			try:
				material.priority=0
				material.autoPriority=False
			except AttributeError:
				pass
			ADSmaterialMap[(ADSmaterialName,extraMaterialProperties)]=material
			EMProNameMaterialMap[EMProMaterialName]=material
		else:
			EMProMaterialName=material.name
		self.materials["simulation_box"]=material
		layerEMProMaterialNameMap["simulation_box"]=EMProMaterialName
		ADSmaterialName=["Copper","top_layer"][materialForEachLayer]
		extraMaterialProperties=(160,3.5001e-05,False,False) # (priority,thickness,modelTypeForMetals,convertedToResistance)
		material=ADSmaterialMap.get((ADSmaterialName,extraMaterialProperties),None)
		if material == None:
			EMProMaterialName = self._getEMProMaterialName(ADSmaterialName,ADSmaterialMap,extraMaterialProperties,ADSmaterialsNo1to1)
			material=self.session.create_material(name=EMProMaterialName, color=(0,100,0,255), conductivity=58700000, imag_conductivity=0, permeability=1)
			self._setModelTypeForMetals(material,False)
			try:
				material.priority=160
				material.autoPriority=False
			except AttributeError:
				pass
			ADSmaterialMap[(ADSmaterialName,extraMaterialProperties)]=material
			EMProNameMaterialMap[EMProMaterialName]=material
		else:
			EMProMaterialName=material.name
		self.materials["top_layer"]=material
		layerEMProMaterialNameMap["top_layer"]=EMProMaterialName
		ADSmaterialName=["Copper","bottom_layer"][materialForEachLayer]
		extraMaterialProperties=(160,3.5001e-05,False,False) # (priority,thickness,modelTypeForMetals,convertedToResistance)
		material=ADSmaterialMap.get((ADSmaterialName,extraMaterialProperties),None)
		if material == None:
			EMProMaterialName = self._getEMProMaterialName(ADSmaterialName,ADSmaterialMap,extraMaterialProperties,ADSmaterialsNo1to1)
			material=self.session.create_material(name=EMProMaterialName, color=(30,144,255,255), conductivity=58700000, imag_conductivity=0, permeability=1)
			self._setModelTypeForMetals(material,False)
			try:
				material.priority=160
				material.autoPriority=False
			except AttributeError:
				pass
			ADSmaterialMap[(ADSmaterialName,extraMaterialProperties)]=material
			EMProNameMaterialMap[EMProMaterialName]=material
		else:
			EMProMaterialName=material.name
		self.materials["bottom_layer"]=material
		layerEMProMaterialNameMap["bottom_layer"]=EMProMaterialName
		ADSmaterialName=["Copper","drill_plated_bottom_top"][materialForEachLayer]
		extraMaterialProperties=(64,None,False,False) # (priority,thickness,modelTypeForMetals,convertedToResistance)
		material=ADSmaterialMap.get((ADSmaterialName,extraMaterialProperties),None)
		if material == None:
			EMProMaterialName = self._getEMProMaterialName(ADSmaterialName,ADSmaterialMap,extraMaterialProperties,ADSmaterialsNo1to1)
			material=self.session.create_material(name=EMProMaterialName, color=(255,0,0,255), conductivity=58700000, imag_conductivity=0, permeability=1)
			self._setModelTypeForMetals(material,False)
			try:
				material.priority=64
				material.autoPriority=False
			except AttributeError:
				pass
			ADSmaterialMap[(ADSmaterialName,extraMaterialProperties)]=material
			EMProNameMaterialMap[EMProMaterialName]=material
		else:
			EMProMaterialName=material.name
		self.materials["drill_plated_bottom_top"]=material
		layerEMProMaterialNameMap["drill_plated_bottom_top"]=EMProMaterialName
		ADSmaterialName=["FR_4","__SubstrateLayer1"][materialForEachLayer]
		extraMaterialProperties=(50,None,None,False) # (priority,thickness,modelTypeForMetals,convertedToResistance)
		material=ADSmaterialMap.get((ADSmaterialName,extraMaterialProperties),None)
		if material == None:
			EMProMaterialName = self._getEMProMaterialName(ADSmaterialName,ADSmaterialMap,extraMaterialProperties,ADSmaterialsNo1to1)
			material=self.session.create_material(name=EMProMaterialName, color=(202,225,255,128), permittivity=1, losstangent=0.01, permeability=1, use_djordjevic=True, lowfreq=1000, evalfreq=1000000000, highfreq=1000000000000)
			try:
				material.priority=50
				material.autoPriority=False
			except AttributeError:
				pass
			ADSmaterialMap[(ADSmaterialName,extraMaterialProperties)]=material
			EMProNameMaterialMap[EMProMaterialName]=material
		else:
			EMProMaterialName=material.name
		self.materials["__SubstrateLayer1"]=material
		layerEMProMaterialNameMap["__SubstrateLayer1"]=EMProMaterialName
		self.substratePartNameMap["__SubstrateLayer1"]=ADSmaterialName
		self.substrateLayers.append("__SubstrateLayer1")
		self.numberSubstratePartNameMap()
		if getSessionVersion(self.session) >= 6:
			self.session.appendUniqueMaterials(EMProNameMaterialMap)
		else:
			for name,material in EMProNameMaterialMap.items():
				empro.activeProject.materials().append(material)
				EMProNameMaterialMap[name] = empro.activeProject.materials().at(empro.activeProject.materials().size()-1)
		self.materials={}
		for layerName in layerEMProMaterialNameMap.keys():
			self.materials[layerName]=EMProNameMaterialMap.get(layerEMProMaterialNameMap.get(layerName,None),None)
		# End of create_materials
	def numberSubstratePartNameMap(self):
		materialCount={}
		for m in self.substratePartNameMap.keys():
			materialCount[self.substratePartNameMap[m]] = materialCount.get(self.substratePartNameMap[m],0) + 1
		multipleUsedMaterials = [m for m in materialCount.keys() if materialCount[m] > 1]
		for layer in self.substrateLayers:
			mat=self.substratePartNameMap.get(layer,None)
			if mat in multipleUsedMaterials:
				self.substratePartNameMap[layer]+=' '+str(materialCount[mat])
				materialCount[mat]-=1
	def setBoundaryConditions(self):
		pass
		# End of setBoundaryConditions
	def setPortWarnings(self,includeInvalidPorts):
		if includeInvalidPorts:
			self.session.warnings.append("No suitable implicit reference has been found for port \"J1_1\". The minus pin has therefore been colocated with the plus pin and will need to be corrected by hand.")
		if includeInvalidPorts:
			self.session.warnings.append("No suitable implicit reference has been found for port \"J1_2\". The minus pin has therefore been colocated with the plus pin and will need to be corrected by hand.")
		if includeInvalidPorts:
			self.session.warnings.append("No suitable implicit reference has been found for port \"J1_3\". The minus pin has therefore been colocated with the plus pin and will need to be corrected by hand.")
		if includeInvalidPorts:
			self.session.warnings.append("No suitable implicit reference has been found for port \"J1_4\". The minus pin has therefore been colocated with the plus pin and will need to be corrected by hand.")
		if includeInvalidPorts:
			self.session.warnings.append("No suitable implicit reference has been found for port \"J1_5\". The minus pin has therefore been colocated with the plus pin and will need to be corrected by hand.")
		if includeInvalidPorts:
			self.session.warnings.append("No suitable implicit reference has been found for port \"P1_1\". The minus pin has therefore been colocated with the plus pin and will need to be corrected by hand.")
		if includeInvalidPorts:
			self.session.warnings.append("No suitable implicit reference has been found for port \"P2_1\". The minus pin has therefore been colocated with the plus pin and will need to be corrected by hand.")
		if includeInvalidPorts:
			self.session.warnings.append("No suitable implicit reference has been found for port \"P3_1\". The minus pin has therefore been colocated with the plus pin and will need to be corrected by hand.")
		if includeInvalidPorts:
			self.session.warnings.append("No suitable implicit reference has been found for port \"P4_1\". The minus pin has therefore been colocated with the plus pin and will need to be corrected by hand.")
		if includeInvalidPorts:
			self.session.warnings.append("No suitable implicit reference has been found for port \"U1_1\". The minus pin has therefore been colocated with the plus pin and will need to be corrected by hand.")
		if includeInvalidPorts:
			self.session.warnings.append("No suitable implicit reference has been found for port \"U1_2\". The minus pin has therefore been colocated with the plus pin and will need to be corrected by hand.")
		if includeInvalidPorts:
			self.session.warnings.append("No suitable implicit reference has been found for port \"U1_3\". The minus pin has therefore been colocated with the plus pin and will need to be corrected by hand.")
		if includeInvalidPorts:
			self.session.warnings.append("No suitable implicit reference has been found for port \"U1_4\". The minus pin has therefore been colocated with the plus pin and will need to be corrected by hand.")
		if includeInvalidPorts:
			self.session.warnings.append("No suitable implicit reference has been found for port \"U1_5\". The minus pin has therefore been colocated with the plus pin and will need to be corrected by hand.")
		if includeInvalidPorts:
			self.session.warnings.append("No suitable implicit reference has been found for port \"U1_6\". The minus pin has therefore been colocated with the plus pin and will need to be corrected by hand.")
		if includeInvalidPorts:
			self.session.warnings.append("No suitable implicit reference has been found for port \"U1_7\". The minus pin has therefore been colocated with the plus pin and will need to be corrected by hand.")
		if includeInvalidPorts:
			self.session.warnings.append("No suitable implicit reference has been found for port \"U1_8\". The minus pin has therefore been colocated with the plus pin and will need to be corrected by hand.")
		if includeInvalidPorts:
			self.session.warnings.append("No suitable implicit reference has been found for port \"U1_9\". The minus pin has therefore been colocated with the plus pin and will need to be corrected by hand.")
		if includeInvalidPorts:
			self.session.warnings.append("No suitable implicit reference has been found for port \"U1_10\". The minus pin has therefore been colocated with the plus pin and will need to be corrected by hand.")
		if includeInvalidPorts:
			self.session.warnings.append("No suitable implicit reference has been found for port \"U1_11\". The minus pin has therefore been colocated with the plus pin and will need to be corrected by hand.")
		if includeInvalidPorts:
			self.session.warnings.append("No suitable implicit reference has been found for port \"U2_1\". The minus pin has therefore been colocated with the plus pin and will need to be corrected by hand.")
		if includeInvalidPorts:
			self.session.warnings.append("No suitable implicit reference has been found for port \"U2_2\". The minus pin has therefore been colocated with the plus pin and will need to be corrected by hand.")
		if includeInvalidPorts:
			self.session.warnings.append("No suitable implicit reference has been found for port \"U2_3\". The minus pin has therefore been colocated with the plus pin and will need to be corrected by hand.")
		if includeInvalidPorts:
			self.session.warnings.append("No suitable implicit reference has been found for port \"U2_4\". The minus pin has therefore been colocated with the plus pin and will need to be corrected by hand.")
		if includeInvalidPorts:
			self.session.warnings.append("No suitable implicit reference has been found for port \"U2_5\". The minus pin has therefore been colocated with the plus pin and will need to be corrected by hand.")
		if includeInvalidPorts:
			self.session.warnings.append("No suitable implicit reference has been found for port \"U2_6\". The minus pin has therefore been colocated with the plus pin and will need to be corrected by hand.")
		if includeInvalidPorts:
			self.session.warnings.append("No suitable implicit reference has been found for port \"U2_7\". The minus pin has therefore been colocated with the plus pin and will need to be corrected by hand.")
		if includeInvalidPorts:
			self.session.warnings.append("No suitable implicit reference has been found for port \"U2_8\". The minus pin has therefore been colocated with the plus pin and will need to be corrected by hand.")
		if includeInvalidPorts:
			self.session.warnings.append("No suitable implicit reference has been found for port \"U2_9\". The minus pin has therefore been colocated with the plus pin and will need to be corrected by hand.")
		if includeInvalidPorts:
			self.session.warnings.append("No suitable implicit reference has been found for port \"U2_10\". The minus pin has therefore been colocated with the plus pin and will need to be corrected by hand.")
		if includeInvalidPorts:
			self.session.warnings.append("No suitable implicit reference has been found for port \"U2_11\". The minus pin has therefore been colocated with the plus pin and will need to be corrected by hand.")
		if includeInvalidPorts:
			self.session.warnings.append("No suitable implicit reference has been found for port \"U3_1\". The minus pin has therefore been colocated with the plus pin and will need to be corrected by hand.")
		if includeInvalidPorts:
			self.session.warnings.append("No suitable implicit reference has been found for port \"U3_2\". The minus pin has therefore been colocated with the plus pin and will need to be corrected by hand.")
		if includeInvalidPorts:
			self.session.warnings.append("No suitable implicit reference has been found for port \"U3_3\". The minus pin has therefore been colocated with the plus pin and will need to be corrected by hand.")
		if includeInvalidPorts:
			self.session.warnings.append("No suitable implicit reference has been found for port \"U3_4\". The minus pin has therefore been colocated with the plus pin and will need to be corrected by hand.")
		if includeInvalidPorts:
			self.session.warnings.append("No suitable implicit reference has been found for port \"U3_5\". The minus pin has therefore been colocated with the plus pin and will need to be corrected by hand.")
		if includeInvalidPorts:
			self.session.warnings.append("No suitable implicit reference has been found for port \"U3_6\". The minus pin has therefore been colocated with the plus pin and will need to be corrected by hand.")
		if includeInvalidPorts:
			self.session.warnings.append("No suitable implicit reference has been found for port \"U3_7\". The minus pin has therefore been colocated with the plus pin and will need to be corrected by hand.")
		if includeInvalidPorts:
			self.session.warnings.append("No suitable implicit reference has been found for port \"U3_8\". The minus pin has therefore been colocated with the plus pin and will need to be corrected by hand.")
		if includeInvalidPorts:
			self.session.warnings.append("No suitable implicit reference has been found for port \"U3_9\". The minus pin has therefore been colocated with the plus pin and will need to be corrected by hand.")
		if includeInvalidPorts:
			self.session.warnings.append("No suitable implicit reference has been found for port \"U3_10\". The minus pin has therefore been colocated with the plus pin and will need to be corrected by hand.")
		if includeInvalidPorts:
			self.session.warnings.append("No suitable implicit reference has been found for port \"U3_11\". The minus pin has therefore been colocated with the plus pin and will need to be corrected by hand.")
		pass
		# End of setPortWarnings
	def initNetlists(self):
		netlistNames = ['net_0_GND___emcosim_J1_2___emcosim_J1_3___emcosim_J1_4___emcosim_J1_5___emcosim_U1_11___emcosim_U1_2___emcosim_U1_3___emcosim_U1_4___emcosim_U1_7___emcosim_U1_8___emcosim_U1_9___emcosim_U2_11___emcosim_U2_2___emcosim_U2_3___emcosim_U2_4___emcosim_U2_7___emcosim_U2_8___emcosim_U2_9___emcosim_U3_11___emcosim_U3_2___emcosim_U3_3___emcosim_U3_4___emcosim_U3_7___emcosim_U3_8___emcosim_U3_9','net_1_0deg___emcosim_U1_1___emcosim_U2_6','net_2_Ant3___emcosim_P3_1___emcosim_U3_6','net_3_Ant2___emcosim_P2_1___emcosim_U1_10','net_4_90deg___emcosim_U2_10___emcosim_U3_1','net_5_Ant1___emcosim_P1_1___emcosim_U1_6','net_6_Radio___emcosim_J1_1___emcosim_U2_1','net_7_Ant4___emcosim_P4_1___emcosim_U3_10','net_8_NetR2_2___emcosim_U2_5','net_9_NetR1_2___emcosim_U1_5','net_10_NetR3_2___emcosim_U3_5']
		if getSessionVersion(self.session) >= 5:
			self.session.initNetlists(netlistNames)
			return
		self.groupList = []
		try:
			for i in netlistNames:
				g = empro.core.ShortcutGroup(i)
				self.groupList.append(g)
		except:
			pass
	def addShortcut(self,netId,part):
		if getSessionVersion(self.session) >= 5:
			self.session.addShortcut(netId,part)
			return
		try:
			s = empro.core.Shortcut(part)
			self.groupList[netId].append(s)
		except:
			pass
	def addShortcutsToProject(self):
		if getSessionVersion(self.session) >= 5:
			self.session.addShortcutsToProject()
			return
		try:
			for g in self.groupList:
				empro.activeProject.shortcuts().append(g)
		except:
			pass

	def ads_import(self,usedFlow="ADS",topAssembly=None,demoMode=False,includeInvalidPorts=True,suppressNotification=False,materialForEachLayer=False):
		if getSessionVersion(self.session) >= 1:
			self.session.prepare_import()
		self.create_materials(materialForEachLayer=materialForEachLayer)
		self.create_parameters()
		if topAssembly != None:
			topAssemblyShouldBeAdded = False
		else:
			topAssembly = empro.geometry.Assembly()
			topAssembly.name = usedFlow+'_import'
			if demoMode:
				empro.activeProject.geometry.append(topAssembly)
				topAssemblyShouldBeAdded = False
			else:
				topAssemblyShouldBeAdded = True
		param_list = empro.activeProject.parameters
		param_list.setFormula( "lateralExtension", "0 um")
		param_list.setFormula( "verticalExtension", "0 um")
		self.create_bondwire_definitions()
		self.setBoundaryConditions()
		symbPinData = self.create_geometry(topAssembly)
		self.create_ports( topAssembly, includeInvalidPorts, symbPinData )
		if get_ads_import_version() >= 11 :
			Expr=empro.core.Expression
			if topAssembly != None:
				bbox_geom = topAssembly.boundingBox()
			else:
				bbox_geom = empro.activeProject.geometry.boundingBox()
			param_list = empro.activeProject.parameters
			param_list.setFormula( "xLowerBoundingBox", str(bbox_geom.lower.x.formula()) +" m - xLowerExtension" )
			param_list.setFormula( "xUpperBoundingBox", str(bbox_geom.upper.x.formula()) +" m + xUpperExtension" )
			param_list.setFormula( "yLowerBoundingBox", str(bbox_geom.lower.y.formula()) +" m - yLowerExtension" )
			param_list.setFormula( "yUpperBoundingBox", str(bbox_geom.upper.y.formula()) +" m + yUpperExtension" )
			param_list.setFormula( "zLowerBoundingBox", str(bbox_geom.lower.z.formula()) +" m - zLowerExtension" )
			param_list.setFormula( "zUpperBoundingBox", str(bbox_geom.upper.z.formula()) +" m + zUpperExtension" )
			param_list.setFormula( "toggleExtensionToBoundingBox", "1" )
		param_list.setFormula( "lateralExtension", "3000 um")
		param_list.setFormula("verticalExtension", "3000 um")
		self.addShortcutsToProject()
		if topAssemblyShouldBeAdded:
			empro.activeProject.geometry.append(topAssembly)
			self.session.adjust_view()
		self.session.renumber_waveguides()
		if getSessionVersion(self.session) >= 10:
			self.session.post_import()
		if not suppressNotification:
			self.session.notify_success()
		return self.session.warnings
		#End of ads_import method

	def create_geometry(self,topAssembly):
		V=empro.geometry.Vector3d
		L=empro.geometry.Line
		unit2meterFactor = 1e-06
		symbPinData = None
		mask_heights=self.getMaskHeights()
		mask_heights_parameterized=self.getMaskHeightsParameterized()
		s3dc_files={}
		s3dc_files["libS3D.xml"]="eJyzCTZ2cbbjstGH0AAcBANS"
		if hasattr(self.session, "create_3d_components"):
			if get_ads_import_version() >= 11 :
				symbPinData = self.session.create_3d_components(s3dc_files, mask_heights, topAssembly, unit2meterFactor)
			else:
				try:
					self.session.create_3d_components(s3dc_files, mask_heights,topAssembly)
				except TypeError:
					self.session.create_3d_components(s3dc_files, mask_heights)
		assembly=empro.geometry.Assembly()
		assembly.name="bondwires"
		assembly=empro.geometry.Assembly()
		part=empro.geometry.Model()
		simBox = empro.geometry.Box( _createIfToggleExtensionToBoundingBoxExpression("xUpperBoundingBox-xLowerBoundingBox", "abs((0.000216606-xLowerExtension)-(0.099808792+xUpperExtension))"), _createIfToggleExtensionToBoundingBoxExpression("zUpperBoundingBox-zLowerBoundingBox", "((((stack_Antenna_layer_7_Z) + (zUpperExtension)) - ((stack_Antenna_layer_1_Z) - (zLowerExtension))))"), _createIfToggleExtensionToBoundingBoxExpression("yUpperBoundingBox-yLowerBoundingBox" , " abs((6.4287e-05-yLowerExtension)-(0.099656473+yUpperExtension))"))
		part.recipe.append(simBox)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(_createIfToggleExtensionToBoundingBoxExpression("(xUpperBoundingBox+xLowerBoundingBox)/2", "(0.099808792+xUpperExtension+0.000216606-xLowerExtension)/2"), _createIfToggleExtensionToBoundingBoxExpression("(yUpperBoundingBox+yLowerBoundingBox)/2", "(0.099656473+yUpperExtension+6.4287e-05-yLowerExtension)/2"), _createIfToggleExtensionToBoundingBoxExpression("zLowerBoundingBox","(((stack_Antenna_layer_1_Z) - (zLowerExtension)) - (0))")))
		part.name="Simulation box"
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=0
		empro.toolkit.applyMaterial(part,self.materials["simulation_box"])
		assembly.append(part)
		assembly.name="simulation_box"
		self.session.hide_part(assembly)
		topAssembly.append(assembly)
		self.session.adjust_view()
		assembly=empro.geometry.Assembly()
		pointString='0.099808792+xUpperExtension#6.4287e-05-yLowerExtension;0.099808792+xUpperExtension#0.099656473+yUpperExtension;0.000216606-xLowerExtension#0.099656473+yUpperExtension;0.000216606-xLowerExtension#6.4287e-05-yLowerExtension'
		sketch = self._create_sketch(pointString)
		sketch.constraintManager().append(empro.geometry.FixedPositionConstraint("vertex0",V(_createIfToggleExtensionToBoundingBoxExpression("xLowerBoundingBox","0.000216606-xLowerExtension"),_createIfToggleExtensionToBoundingBoxExpression("yLowerBoundingBox","6.4287e-05-yLowerExtension"),0)))
		sketch.constraintManager().append(empro.geometry.FixedPositionConstraint("vertex1",V(_createIfToggleExtensionToBoundingBoxExpression("xUpperBoundingBox","0.099808792+xUpperExtension"),_createIfToggleExtensionToBoundingBoxExpression("yLowerBoundingBox","6.4287e-05-yLowerExtension"),0)))
		sketch.constraintManager().append(empro.geometry.FixedPositionConstraint("vertex2",V(_createIfToggleExtensionToBoundingBoxExpression("xUpperBoundingBox","0.099808792+xUpperExtension"),_createIfToggleExtensionToBoundingBoxExpression("yUpperBoundingBox","0.099656473+yUpperExtension"),0)))
		sketch.constraintManager().append(empro.geometry.FixedPositionConstraint("vertex3",V(_createIfToggleExtensionToBoundingBoxExpression("xLowerBoundingBox","0.000216606-xLowerExtension"),_createIfToggleExtensionToBoundingBoxExpression("yUpperBoundingBox","0.099656473+yUpperExtension"),0)))
		part=empro.geometry.Model()
		part.recipe.append(empro.geometry.Extrude(sketch,"(stack_Antenna_layer_5_Z) - (stack_Antenna_layer_3_Z)",V(0,0,1)))
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(stack_Antenna_layer_3_Z) - (0)"))
		part.name=self.substratePartNameMap["__SubstrateLayer1"]
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=50
		empro.toolkit.applyMaterial(part,self.materials["__SubstrateLayer1"])
		self.session.hide_part(part)
		assembly.append(part)
		assembly.name="substrate"
		topAssembly.append(assembly)
		assembly=empro.geometry.Assembly()
		pointStrings=['0.089808792#6.4287e-05;0.089808792#0.008860381;0.090162584#0.009710495;0.091012698#0.010064288;0.099808792#0.010064288;0.099808792#0.089656473;0.09090468#0.089661533;0.090125132#0.090049322;0.089808792#0.09086038;0.089808792#0.099656473;0.010216606#0.099656473;0.010216606#0.09086038;0.009862814#0.090010265;0.0090127#0.089656473;0.000216606#0.089656473;0.000216606#0.010064288;0.0090127#0.010064288;0.009862813#0.009710494;0.010216606#0.008860381;0.010216606#6.4287e-05']
		pointStrings.append('0.011098677#0.050243809;0.011309352#0.050358669;0.011550648#0.050358669;0.011761323#0.050243809;0.011849819#0.050243809;0.011897047#0.050285521;0.012180881#0.050371987;0.012465011#0.0502865;0.012666426#0.050025027;0.012666426#0.049694971;0.012465011#0.049433498;0.012180881#0.049348011;0.011897047#0.049434477;0.011849819#0.04947619;0.011761323#0.04947619;0.011550648#0.049361329;0.011309352#0.049361329;0.011098677#0.04947619;0.010379199#0.04947619;0.010379199#0.0429068;0.0032228#0.0429068;0.0032228#0.056813199;0.010379199#0.056813199;0.010379199#0.050243809')
		pointStrings.append('0.049654191#0.089020129;0.049654191#0.0895318;0.043084801#0.0895318;0.043084801#0.096688199;0.056991199#0.096688199;0.056991199#0.0895318;0.050421809#0.0895318;0.050421809#0.08892431;0.050464372#0.08886061;0.050513056#0.088646;0.050474001#0.088449661;0.050421809#0.08837155;0.050421809#0.088195046;0.050490485#0.088062246;0.050506124#0.08784047;0.050426249#0.087632986;0.050164919#0.08743172;0.049835068#0.087431689;0.0495737#0.087632906;0.049488137#0.087916955;0.04957452#0.088200755;0.04963602#0.088281368;0.04957489#0.088362157;0.049491461#0.088701701')
		pointStrings.append('0.049574548#0.011333247;0.049637216#0.011411783;0.049526#0.011617467;0.049486944#0.011813807;0.049526#0.012010146;0.049637216#0.012176592;0.049803662#0.012287809;0.050000002#0.012326864;0.050214298#0.012279821;0.050389514#0.012148168;0.050493298#0.011955135;0.050506486#0.011736369;0.050421812#0.011535496;0.050421812#0.01132345;0.050474004#0.011245339;0.050513059#0.011049;0.050474004#0.010852661;0.050421812#0.01077455;0.050421812#0.010188199;0.056991202#0.010188199;0.056991202#0.0030318;0.043084803#0.0030318;0.043084803#0.010188199;0.049616192#0.010188199;0.049616192#0.010717677;0.049574106#0.010764854;0.049488019#0.011049118')
		pointStrings.append('0.048103495#0.048488765;0.048280791#0.048141167;0.048628391#0.047963874;0.048628391#0.047758309;0.048133356#0.047993731;0.047897931#0.048488765')
		pointStrings.append('0.048019519#0.049046227;0.048274702#0.049299388;0.048628391#0.049422426;0.048628391#0.049216862;0.048386583#0.049123551;0.04819446#0.048932951;0.048103495#0.048691965;0.047897931#0.048691965')
		pointStrings.append('0.048103495#0.051028765;0.048194461#0.050787782;0.048386585#0.050597184;0.048628391#0.050503874;0.048628391#0.050298309;0.048274704#0.050421347;0.048019521#0.050674504;0.047897931#0.051028765')
		pointStrings.append('0.048133354#0.051727003;0.048628391#0.051962426;0.048628391#0.051756862;0.048280789#0.051579567;0.048103495#0.051231965;0.047897931#0.051231965')
		pointStrings.append('0.048831591#0.047963874;0.049072573#0.048054839;0.049263172#0.048246961;0.049356483#0.048488765;0.049562047#0.048488765;0.049439008#0.048135079;0.04918585#0.047879899;0.048831591#0.047758309')
		pointStrings.append('0.049183364#0.050079181;0.049267821#0.050283085;0.049348746#0.050388545;0.049258167#0.050479124;0.049152706#0.0503982;0.048948802#0.050313742;0.048831591#0.050298309;0.048831591#0.050503874;0.049076314#0.050598433;0.049261923#0.050784042;0.049356483#0.051028765;0.049562047#0.051028765;0.049546614#0.050911554;0.049462157#0.050707651;0.049381232#0.05060219;0.049471811#0.050511611;0.049577272#0.050592535;0.049781176#0.050676993;0.049999989#0.050705802;0.050218802#0.050676993;0.050422706#0.050592535;0.050528167#0.050511611;0.050618746#0.05060219;0.050537821#0.050707651;0.050453364#0.050911554;0.050437931#0.051028768;0.050643495#0.051028768;0.050737563#0.050784098;0.050923626#0.050598941;0.051168394#0.050503873;0.051168394#0.050298309;0.051051176#0.050313742;0.050847272#0.0503982;0.050741811#0.050479124;0.050651232#0.050388545;0.050732157#0.050283085;0.050816614#0.050079181;0.050845423#0.049860368;0.050816614#0.049641554;0.050732157#0.049437651;0.050651232#0.04933219;0.050741811#0.049241611;0.050847272#0.049322535;0.051051176#0.049406993;0.051168391#0.049422426;0.051168391#0.049216862;0.050923623#0.049121794;0.050737562#0.048936636;0.050643495#0.048691965;0.050437931#0.048691965;0.050453364#0.048809181;0.050537821#0.049013085;0.050618746#0.049118545;0.050528167#0.049209124;0.0502825#0.049063534;0.049999989#0.049014934;0.049781176#0.049043742;0.049577272#0.0491282;0.049471811#0.049209124;0.049381232#0.049118545;0.049462157#0.049013085;0.049546614#0.048809181;0.049562047#0.048691965;0.049356483#0.048691965;0.049261925#0.048936691;0.049076316#0.049122302;0.048831591#0.049216862;0.048831591#0.049422426;0.048948802#0.049406993;0.049152706#0.049322535;0.049258167#0.049241611;0.049348746#0.04933219;0.049267821#0.049437651;0.049183364#0.049641554;0.049154555#0.049860368')
		pointStrings.append('0.048831591#0.051962426;0.049185852#0.051840836;0.04943901#0.051585653;0.049562047#0.051231965;0.049356483#0.051231965;0.049263173#0.051473772;0.049072574#0.051665896;0.048831591#0.051756862')
		pointStrings.append('0.050643495#0.048488765;0.050736816#0.04824681;0.050927309#0.048054712;0.051168391#0.047963874;0.051168391#0.047758309;0.050814059#0.047879695;0.050560855#0.048135034;0.050437931#0.048488765')
		pointStrings.append('0.050560856#0.0515857;0.050814061#0.05184104;0.051168394#0.051962426;0.051168394#0.051756863;0.050927309#0.051666025;0.050736816#0.051473925;0.050643495#0.051231968;0.050437931#0.051231968')
		pointStrings.append('0.051371591#0.047963874;0.051718797#0.048140753;0.051896483#0.048488765;0.052102047#0.048488765;0.051866548#0.047993627;0.051371591#0.047758309')
		pointStrings.append('0.051371591#0.049422426;0.051725204#0.049299192;0.051980337#0.049046187;0.052102047#0.048691965;0.051896483#0.048691965;0.051805521#0.048932808;0.051613294#0.049123432;0.051371591#0.049216862')
		pointStrings.append('0.051371594#0.050503875;0.051613294#0.050597305;0.05180552#0.050787928;0.051896483#0.051028768;0.052102047#0.051028768;0.051980337#0.050674547;0.051725206#0.050421545;0.051371594#0.050298312')
		pointStrings.append('0.051371594#0.051962423;0.051866551#0.051727106;0.052102047#0.051231968;0.051896483#0.051231968;0.0517188#0.051579981;0.051371594#0.051756861')
		pointStrings.append('0.08738818#0.050025027;0.087589595#0.0502865;0.087873725#0.050371987;0.088157559#0.050285521;0.088204787#0.050243809;0.088314677#0.050243809;0.088525352#0.050358669;0.088766648#0.050358669;0.088977323#0.050243809;0.089722803#0.050243809;0.089722803#0.056813199;0.096879202#0.056813199;0.096879202#0.0429068;0.089722803#0.0429068;0.089722803#0.04947619;0.088977323#0.04947619;0.088766648#0.049361329;0.088525352#0.049361329;0.088314677#0.04947619;0.088204787#0.04947619;0.088157559#0.049434477;0.087873725#0.049348011;0.087589595#0.049433498;0.08738818#0.049694971')
		part = self._create_extrude(pointStrings, "(mask_top_layer_Zmax) - (mask_top_layer_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_top_layer_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 1006)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=160
		empro.toolkit.applyMaterial(part,self.materials["top_layer"])
		assembly.append(part)
		self.addShortcut(0,part)
		self._update_geoProgress()
		pointStrings=['0.010175999#0.043109999;0.010175999#0.049610562;0.011263723#0.049610562;0.011429896#0.049560029;0.011596277#0.049610562;0.012014865#0.049610562;0.012181246#0.04956023;0.012347604#0.049610283;0.012465533#0.049763375;0.012465533#0.049956623;0.012347604#0.050109715;0.012181246#0.050159768;0.012014865#0.050109436;0.011596277#0.050109436;0.011429896#0.050159969;0.011263723#0.050109436;0.010175999#0.050109436;0.010175999#0.05661;0.003426#0.05661;0.003426#0.043109999']
		part = self._create_extrude(pointStrings, "(mask_top_layer_Zmax) - (mask_top_layer_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_top_layer_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 1006)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=160
		empro.toolkit.applyMaterial(part,self.materials["top_layer"])
		assembly.append(part)
		self.addShortcut(5,part)
		pointStrings=['0.049750261#0.087750259;0.049903365#0.08763239;0.050096585#0.087632408;0.050249666#0.087750306;0.050296455#0.087871845;0.050287437#0.0880018;0.050287437#0.089735;0.056788#0.089735;0.056788#0.096484999;0.043288#0.096484999;0.043288#0.089735;0.049788563#0.089735;0.049788563#0.088858768;0.049701741#0.088678922;0.049750669#0.088479795;0.049788563#0.088433232;0.049788563#0.088129504;0.049750741#0.088082893;0.049700139#0.087916649']
		part = self._create_extrude(pointStrings, "(mask_top_layer_Zmax) - (mask_top_layer_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_top_layer_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 1006)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=160
		empro.toolkit.applyMaterial(part,self.materials["top_layer"])
		assembly.append(part)
		self.addShortcut(3,part)
		pointStrings=['0.056788003#0.003235;0.056788003#0.009984999;0.05028744#0.009984999;0.05028744#0.011728743;0.050291438#0.011884973;0.050216055#0.012021943;0.050081993#0.012102384;0.049925663#0.01210445;0.049789523#0.012027578;0.049710548#0.011892648;0.049710187#0.011736305;0.049788566#0.011601039;0.049788566#0.011261768;0.049750547#0.011215289;0.04969989#0.011048953;0.049750565#0.010882723;0.049750565#0.009984999;0.043288002#0.009984999;0.043288002#0.003235']
		part = self._create_extrude(pointStrings, "(mask_top_layer_Zmax) - (mask_top_layer_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_top_layer_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 1006)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=160
		empro.toolkit.applyMaterial(part,self.materials["top_layer"])
		assembly.append(part)
		self.addShortcut(7,part)
		pointStrings=['0.049413325#0.049617364;0.049550976#0.049411355;0.049756985#0.049273704;0.049999989#0.049225368;0.050242993#0.049273704;0.050449002#0.049411355;0.050586653#0.049617364;0.050634989#0.049860368;0.050586653#0.050103372;0.050449002#0.050309381;0.050242993#0.050447032;0.049999989#0.050495368;0.049756985#0.050447032;0.049550976#0.050309381;0.049413325#0.050103372;0.049364989#0.049860368']
		part = self._create_extrude(pointStrings, "(mask_top_layer_Zmax) - (mask_top_layer_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_top_layer_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 1006)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=160
		empro.toolkit.applyMaterial(part,self.materials["top_layer"])
		assembly.append(part)
		self.addShortcut(6,part)
		pointStrings=['0.096676002#0.043109999;0.096676002#0.05661;0.089926003#0.05661;0.089926003#0.050109436;0.088812277#0.050109436;0.088646104#0.050159969;0.088479723#0.050109436;0.088039741#0.050109436;0.08787336#0.050159768;0.087707002#0.050109715;0.087589073#0.049956623;0.087589073#0.049763375;0.087707002#0.049610283;0.08787336#0.04956023;0.088039741#0.049610562;0.088479723#0.049610562;0.088646104#0.049560029;0.088812277#0.049610562;0.089926003#0.049610562;0.089926003#0.043109999']
		part = self._create_extrude(pointStrings, "(mask_top_layer_Zmax) - (mask_top_layer_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_top_layer_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 1006)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=160
		empro.toolkit.applyMaterial(part,self.materials["top_layer"])
		assembly.append(part)
		self.addShortcut(2,part)
		self._update_geoProgress()
		self._setAssemblyMeshSettings(assembly,0,0,0)
		assembly.name="top_layer"
		topAssembly.append(assembly)
		assembly=empro.geometry.Assembly()
		pointStrings=['0.089808792#6.4287e-05;0.089808792#0.008860381;0.090162584#0.009710495;0.091012698#0.010064288;0.099808792#0.010064288;0.099808792#0.089656473;0.091012698#0.089656473;0.090162583#0.090010264;0.089808792#0.09086038;0.089808792#0.099656473;0.010216606#0.099656473;0.010216606#0.09086038;0.009862814#0.090010265;0.0090127#0.089656473;0.000216606#0.089656473;0.000216606#0.010064288;0.0090127#0.010064288;0.009862813#0.009710494;0.010216606#0.008860381;0.010216606#6.4287e-05']
		pointStrings.append('0.010944716#0.050025027;0.011146131#0.0502865;0.011430261#0.050371987;0.011714095#0.050285521;0.011761323#0.050243809;0.011849819#0.050243809;0.012060494#0.050358669;0.012301789#0.050358669;0.012512464#0.050243809;0.017452929#0.050243809;0.01751663#0.050286371;0.018186311#0.050354757;0.018832206#0.050525389;0.019427497#0.050828581;0.019946965#0.051249034;0.020367418#0.051768502;0.02067061#0.052363793;0.020841242#0.053009688;0.020909628#0.053679369;0.020952191#0.05374307;0.020952191#0.066366454;0.020909628#0.066430154;0.020874497#0.066606763;0.020873799#0.066606763;0.020912018#0.067189881;0.021026023#0.067763022;0.021213862#0.068316378;0.021472322#0.068840482;0.02179698#0.069326366;0.022182282#0.069765718;0.022621634#0.07015102;0.023107518#0.070475678;0.023631622#0.070734138;0.024184978#0.070921977;0.024758119#0.071035982;0.025341237#0.071074201;0.025341237#0.071073503;0.025517846#0.071038372;0.025581547#0.070995809;0.029997301#0.070995809;0.0299593#0.0717804;0.0301625#0.0717804;0.0301625#0.071501;0.0325755#0.071501;0.0325755#0.072263;0.0301625#0.072263;0.0301625#0.0719836;0.0299593#0.0719836;0.0299593#0.0730504;0.0301625#0.0730504;0.0301625#0.072771;0.0325755#0.072771;0.0325755#0.073533;0.0301625#0.073533;0.0301625#0.0732536;0.0299593#0.0732536;0.0299593#0.0743204;0.0301625#0.0743204;0.0301625#0.074041;0.0325755#0.074041;0.0325755#0.074168;0.0330835#0.074168;0.0330835#0.070231;0.0342519#0.070231;0.0342519#0.0700278;0.029997301#0.0700278;0.029997301#0.070228191;0.025581547#0.070228191;0.025517846#0.070185628;0.025341237#0.070150497;0.025334145#0.07015705;0.024785762#0.070113893;0.024243965#0.069983817;0.023729185#0.069770589;0.023254101#0.069479457;0.022830409#0.069117591;0.022468543#0.068693899;0.022177411#0.068218815;0.021964183#0.067704035;0.021834107#0.067162238;0.02179095#0.066613855;0.021797503#0.066606763;0.021762372#0.066430154;0.021719809#0.066366454;0.021719809#0.05374307;0.021762372#0.053679369;0.021797503#0.053502761;0.0218013#0.053502761;0.021750724#0.052860118;0.021600236#0.052233299;0.021353549#0.05163774;0.02101673#0.051088102;0.020598077#0.050597923;0.020107897#0.05017927;0.019558259#0.04984245;0.0189627#0.049595763;0.018335882#0.049445276;0.017693239#0.049394699;0.017693239#0.049398497;0.01751663#0.049433627;0.017452929#0.04947619;0.012512464#0.04947619;0.012301789#0.049361329;0.012060493#0.049361329;0.011849819#0.04947619;0.011761323#0.04947619;0.011714095#0.049434477;0.011430261#0.049348011;0.011146131#0.049433498;0.010944716#0.049694971')
		pointStrings.append('0.031409643#0.037403143;0.031501766#0.037099451;0.031651367#0.036819566;0.031852697#0.036574245;0.032187819#0.03631617;0.032577812#0.036155538;0.032997432#0.036104048;0.033417049#0.036155539;0.03380704#0.036316171;0.034142159#0.036574245;0.03434349#0.036819566;0.034493091#0.037099451;0.034585214#0.037403143;0.034615933#0.03771503;0.034612359#0.037718975;0.03464749#0.037895583;0.034690053#0.037959284;0.034690053#0.039555148;0.03464749#0.039618849;0.034612359#0.039795458;0.034608988#0.039795458;0.03465782#0.040291243;0.034802435#0.040767973;0.035037276#0.041207332;0.03535332#0.041592431;0.03573842#0.041908476;0.036177779#0.042143317;0.036654509#0.042287932;0.037150289#0.042336766;0.037646082#0.042287932;0.038122812#0.042143317;0.038562171#0.041908476;0.03894727#0.041592431;0.039263315#0.041207332;0.039498156#0.040767973;0.039642771#0.040291243;0.039691605#0.039795458;0.039739707#0.039375903;0.039900327#0.038985863;0.040158431#0.038650702;0.040403752#0.038449372;0.040683637#0.038299771;0.04098733#0.038207648;0.041299216#0.038176929;0.041303161#0.038180503;0.04147977#0.038145372;0.04154347#0.038102809;0.062169307#0.038102809;0.062233007#0.038145372;0.062825866#0.038207676;0.063397611#0.038355891;0.063924717#0.038622388;0.064384321#0.038993679;0.064755612#0.039453283;0.065022109#0.039980389;0.065170324#0.040552134;0.065232628#0.041144993;0.065275191#0.041208693;0.065275191#0.046997539;0.065232628#0.047061239;0.065183823#0.047516612;0.065076991#0.047955299;0.064876041#0.048359623;0.064593107#0.048711955;0.064240775#0.048994889;0.063836451#0.04919584;0.063397764#0.049302671;0.062942391#0.049351476;0.062878691#0.049394039;0.061698861#0.049394039;0.061698861#0.049193648;0.057406261#0.049193648;0.057406261#0.049396848;0.058574661#0.049396848;0.058574661#0.050793848;0.059082661#0.050793848;0.059082661#0.050666848;0.061495661#0.050666848;0.061495661#0.050946248;0.061698861#0.050946248;0.061698861#0.050161657;0.062878691#0.050161657;0.062942391#0.05020422;0.063119#0.050239351;0.063119#0.050239737;0.063588598#0.05020278;0.064046633#0.050092813;0.064481829#0.049912549;0.064883467#0.049666426;0.065241655#0.049360503;0.065547578#0.049002315;0.065793701#0.048600678;0.065973965#0.048165482;0.066083932#0.047707446;0.066120889#0.047237848;0.066120503#0.047237848;0.066085372#0.047061239;0.066042809#0.046997539;0.066042809#0.041208693;0.066085372#0.041144993;0.066120503#0.040968384;0.066123083#0.040968384;0.066077363#0.040387471;0.065941334#0.03982086;0.065718339#0.039282505;0.065413875#0.038785663;0.065035435#0.038342565;0.064592337#0.037964125;0.064095495#0.037659661;0.06355714#0.037436666;0.062990529#0.037300637;0.062409616#0.037254917;0.062409616#0.037257497;0.062233007#0.037292628;0.062169307#0.037335191;0.04154347#0.037335191;0.04147977#0.037292628;0.041303161#0.037257497;0.041303161#0.037254127;0.040807376#0.037302958;0.040330646#0.037447573;0.039891287#0.037682414;0.039506187#0.037998458;0.039147979#0.038448394;0.03890246#0.038969226;0.038776807#0.039531149;0.038738081#0.040111289;0.038602237#0.040511477;0.038367444#0.040862868;0.038049705#0.041141518;0.037671453#0.041327894;0.037257168#0.041406659;0.036834463#0.041383242;0.036434276#0.041247398;0.036082884#0.041012606;0.035804234#0.040694867;0.035654633#0.040414981;0.03556251#0.040111289;0.035531791#0.039799402;0.035535365#0.039795458;0.035500234#0.039618849;0.035457671#0.039555148;0.035457671#0.037959284;0.035500234#0.037895583;0.035535365#0.037718975;0.035538735#0.037718975;0.035489904#0.037223189;0.035345289#0.036746459;0.035110448#0.0363071;0.034794403#0.035922001;0.034409304#0.035605956;0.033969945#0.035371115;0.033493215#0.035226501;0.032997422#0.035177667;0.032501642#0.035226501;0.032024912#0.035371115;0.031585553#0.035605956;0.031200453#0.035922001;0.030884409#0.0363071;0.030649568#0.036746459;0.030504953#0.037223189;0.030456121#0.037718975;0.030459492#0.037718975;0.030494623#0.037895583;0.030537186#0.037959284;0.030537186#0.039555148;0.030494623#0.039618849;0.030459492#0.039795458;0.030463066#0.039799402;0.030432347#0.040111289;0.030340224#0.040414981;0.030190623#0.040694867;0.029911973#0.041012606;0.029560581#0.041247398;0.029160394#0.041383242;0.028737689#0.041406659;0.028323403#0.041327894;0.027945151#0.041141518;0.027627412#0.040862868;0.02739262#0.040511476;0.027256776#0.040111289;0.02721805#0.039531148;0.027092397#0.038969226;0.026846878#0.038448394;0.026488669#0.037998458;0.02610357#0.037682414;0.025664211#0.037447573;0.025187481#0.037302958;0.024691696#0.037254127;0.024691696#0.037257497;0.024515087#0.037292628;0.024451386#0.037335191;0.020419375#0.037335191;0.020355674#0.037292628;0.020179066#0.037257497;0.020173104#0.037263078;0.01958133#0.037224292;0.01899382#0.037107429;0.01842659#0.036914879;0.017889347#0.036649939;0.017391281#0.036317144;0.016940914#0.035922184;0.016545954#0.035471816;0.016213158#0.03497375;0.015948218#0.034436507;0.015755668#0.033869277;0.015638805#0.033281767;0.01560002#0.032689993;0.0156056#0.032684032;0.015570469#0.032507423;0.015527906#0.032443722;0.015527906#0.032011795;0.015570469#0.031948095;0.0156056#0.031771486;0.015600139#0.031765654;0.015638417#0.03118166;0.015753733#0.030601928;0.015943732#0.030042206;0.016205167#0.029512072;0.016533559#0.0290206;0.016923291#0.028576194;0.017367697#0.028186461;0.017859169#0.02785807;0.018389303#0.027596635;0.018949022#0.027406636;0.019528754#0.02729132;0.020112749#0.027253042;0.020118581#0.027258503;0.020295189#0.027223372;0.02035889#0.027180809;0.024518391#0.027180809;0.024582092#0.027223372;0.024758701#0.027258503;0.024762645#0.027254929;0.025074532#0.027285648;0.025378225#0.027377771;0.02565811#0.027527372;0.025903431#0.027728702;0.026182534#0.028102491;0.026341465#0.028540805;0.02637026#0.02900695;0.026419091#0.029502732;0.026563706#0.029979463;0.026798547#0.030418822;0.027114591#0.030803921;0.027499691#0.031119966;0.02793905#0.031354806;0.02841578#0.031499421;0.028911573#0.031548255;0.029407353#0.031499421;0.029884083#0.031354806;0.030323442#0.031119966;0.030708542#0.030803921;0.031024586#0.030418822;0.031259427#0.029979463;0.031404042#0.029502732;0.031452873#0.029006947;0.031449503#0.029006947;0.031414372#0.028830339;0.031371809#0.028766638;0.031371809#0.024414013;0.031414372#0.024350312;0.031449503#0.024173703;0.031445929#0.024169759;0.031476648#0.023857872;0.031568771#0.023554179;0.031718372#0.023274294;0.031919702#0.023028974;0.032254824#0.022770899;0.032644817#0.022610267;0.033064437#0.022558776;0.033484055#0.022610268;0.033874045#0.0227709;0.034209165#0.023028974;0.034410495#0.023274294;0.034560096#0.023554179;0.034652219#0.023857872;0.034682938#0.024169759;0.034679364#0.024173703;0.034714495#0.024350312;0.034757058#0.024414013;0.034757058#0.028755574;0.034714495#0.028819274;0.034679364#0.028995883;0.034675994#0.028995883;0.034724825#0.029491668;0.03486944#0.029968398;0.035104281#0.030407757;0.035420325#0.030792857;0.035805425#0.031108901;0.036244784#0.031343742;0.036721514#0.031488357;0.037217294#0.031537191;0.037713087#0.031488357;0.038189817#0.031343742;0.038629176#0.031108901;0.039014276#0.030792857;0.03933032#0.030407757;0.039565161#0.029968398;0.039709776#0.029491668;0.039758607#0.028995888;0.039758612#0.028995888;0.039787482#0.028533798;0.039947927#0.028099579;0.040225436#0.027728702;0.040470757#0.027527372;0.040750642#0.027377771;0.041054335#0.027285648;0.041366222#0.027254929;0.041370166#0.027258503;0.041546775#0.027223372;0.041610476#0.027180809;0.0601218#0.027180809;0.0601218#0.0279654;0.060325#0.0279654;0.060325#0.027686;0.062738#0.027686;0.062738#0.027813;0.063246#0.027813;0.063246#0.026416;0.0644144#0.026416;0.0644144#0.0262128;0.0601218#0.0262128;0.0601218#0.026413191;0.041610476#0.026413191;0.041546775#0.026370628;0.041370166#0.026335497;0.041370166#0.026332127;0.040874381#0.026380958;0.040397651#0.026525573;0.039958292#0.026760414;0.039573192#0.027076458;0.039257148#0.027461558;0.039022307#0.027900917;0.038877692#0.028377647;0.038828861#0.028873427;0.038828856#0.028873427;0.038799986#0.029335517;0.038639541#0.029769737;0.038362031#0.030140613;0.038026909#0.030398688;0.037636917#0.03055932;0.037217297#0.03061081;0.036797679#0.030559319;0.036407689#0.030398687;0.036072569#0.030140613;0.035871239#0.029895292;0.035721638#0.029615407;0.035629515#0.029311714;0.035598796#0.028999828;0.03560237#0.028995883;0.035567239#0.028819274;0.035524676#0.028755574;0.035524676#0.024414013;0.035567239#0.024350312;0.03560237#0.024173703;0.03560574#0.024173703;0.035556909#0.023677918;0.035412294#0.023201188;0.035177453#0.022761829;0.034861409#0.022376729;0.034476309#0.022060685;0.03403695#0.021825844;0.03356022#0.021681229;0.033064427#0.021632395;0.032568647#0.021681229;0.032091917#0.021825844;0.031652558#0.022060685;0.031267458#0.022376729;0.030951414#0.022761829;0.030716573#0.023201188;0.030571958#0.023677918;0.030523127#0.024173703;0.030526497#0.024173703;0.030561628#0.024350312;0.030604191#0.024414013;0.030604191#0.028766638;0.030561628#0.028830339;0.030526497#0.029006947;0.030530071#0.029010892;0.030499352#0.029322779;0.030407229#0.029626471;0.030257628#0.029906356;0.030056298#0.030151677;0.029721176#0.030409752;0.029331183#0.030570384;0.028911563#0.030621874;0.028491945#0.030570383;0.028101955#0.030409752;0.027766836#0.030151677;0.027487733#0.029777889;0.027328801#0.029339575;0.027300006#0.02887343;0.027251175#0.028377647;0.02710656#0.027900917;0.026871719#0.027461558;0.026555675#0.027076458;0.026170575#0.026760414;0.025731216#0.026525573;0.025254486#0.026380958;0.024758701#0.026332127;0.024758701#0.026335497;0.024582092#0.026370628;0.024518391#0.026413191;0.02035889#0.026413191;0.020295189#0.026370628;0.020118581#0.026335497;0.020118581#0.026332718;0.019408678#0.026379249;0.018710923#0.026518039;0.018037256#0.026746721;0.017399198#0.027061376;0.01680767#0.027456623;0.016272794#0.027925697;0.01580372#0.028460573;0.015408473#0.029052103;0.015093818#0.029690159;0.014865137#0.030363828;0.014726346#0.031061584;0.014679816#0.031771486;0.014682594#0.031771486;0.014717725#0.031948095;0.014760288#0.032011795;0.014760288#0.032443722;0.014717725#0.032507423;0.014682594#0.032684032;0.014679686#0.032684032;0.014726735#0.033401846;0.014867072#0.034107377;0.015098301#0.034788554;0.015416464#0.035433721;0.015816115#0.036031841;0.016290417#0.03657268;0.016831257#0.037046982;0.017429376#0.037446633;0.018074543#0.037764796;0.018755721#0.037996025;0.019461251#0.038136363;0.020179066#0.038183411;0.020179066#0.038180503;0.020355674#0.038145372;0.020419375#0.038102809;0.024451386#0.038102809;0.024515087#0.038145372;0.024691696#0.038180503;0.02469564#0.038176929;0.025007527#0.038207648;0.025311219#0.038299771;0.025591105#0.038449372;0.025836425#0.038650702;0.02609453#0.038985863;0.02625515#0.039375904;0.026303252#0.03979546;0.026352086#0.040291243;0.026496701#0.040767973;0.026731542#0.041207332;0.027047586#0.041592431;0.027432686#0.041908476;0.027872045#0.042143317;0.028348775#0.042287932;0.028844568#0.042336766;0.029340348#0.042287932;0.029817078#0.042143317;0.030256437#0.041908476;0.030641536#0.041592431;0.030957581#0.041207332;0.031192422#0.040767973;0.031337037#0.040291243;0.031385868#0.039795458;0.031382498#0.039795458;0.031347367#0.039618849;0.031304804#0.039555148;0.031304804#0.037959284;0.031347367#0.037895583;0.031382498#0.037718975;0.031378924#0.03771503')
		pointStrings.append('0.025852798#0.079224182;0.025984269#0.079771794;0.026199785#0.080292097;0.026494042#0.080772279;0.026859794#0.081200518;0.027288033#0.081566271;0.027768215#0.081860527;0.028288518#0.082076044;0.02883613#0.082207514;0.029397566#0.0822517;0.029397566#0.082249503;0.029574175#0.082214372;0.029637876#0.082171809;0.045217748#0.082171809;0.045281449#0.082214372;0.045458057#0.082249503;0.045466805#0.082241418;0.046097751#0.082291075;0.046721692#0.082440869;0.047314521#0.082686426;0.047861637#0.083021701;0.048349568#0.083438431;0.048766298#0.083926363;0.049101573#0.084473479;0.04934713#0.085066307;0.049496924#0.085690248;0.049546581#0.086321194;0.049538496#0.086329942;0.049573627#0.08650655;0.04961619#0.086570251;0.04961619#0.087585413;0.049525997#0.087720396;0.049486942#0.087916736;0.049525997#0.088113075;0.04961619#0.088248058;0.04961619#0.088314677;0.04957445#0.088361862;0.049490934#0.088701758;0.049645296#0.089015886;0.049958126#0.089156899;0.050289741#0.089068701;0.050491183#0.08879091;0.050490607#0.088500383;0.050425498#0.088361946;0.050383808#0.088314677;0.050383808#0.088248058;0.050474001#0.088113075;0.050513056#0.087916736;0.050474001#0.087720396;0.050383808#0.087585413;0.050383808#0.086570251;0.050426371#0.08650655;0.050461502#0.086329942;0.050463351#0.086329942;0.050420529#0.085676621;0.0502928#0.085034476;0.050082346#0.0844145;0.049792768#0.083827295;0.049429025#0.083282912;0.048997334#0.082790665;0.048505087#0.082358974;0.047960704#0.081995231;0.047373499#0.081705653;0.046753523#0.081495199;0.046111378#0.08136747;0.045458057#0.081324648;0.045458057#0.081326497;0.045281449#0.081361628;0.045217748#0.081404191;0.029637876#0.081404191;0.029574175#0.081361628;0.029005545#0.081301221;0.028457204#0.081160089;0.027951618#0.080905178;0.027510905#0.080549407;0.027238993#0.080231041;0.027020233#0.079874057;0.026860012#0.079487248;0.026759601#0.079056158;0.026735042#0.078613483;0.026773901#0.078171751;0.027600145#0.076755837;0.02912348#0.076157;0.029426469#0.076118372;0.02949017#0.076075809;0.029997301#0.076075809;0.029997301#0.0762762;0.0342519#0.0762762;0.0342519#0.076073;0.0330835#0.076073;0.0330835#0.074676;0.0325755#0.074676;0.0325755#0.074803;0.0301625#0.074803;0.0301625#0.0745236;0.0299593#0.0745236;0.0299593#0.07499654;0.029997301#0.075218387;0.029907497#0.075308191;0.02949017#0.075308191;0.029426469#0.075265628;0.029250891#0.0752307;0.029250894#0.075229364;0.02908128#0.075234686;0.027001949#0.07606103;0.025875776#0.077994473;0.025809087#0.078662936;0.025808648#0.078663178')
		pointStrings.append('0.0385445#0.071501;0.0385445#0.0717804;0.0387477#0.0717804;0.0387477#0.070995809;0.03929779#0.070995809;0.03929779#0.071115199;0.04064939#0.071115199;0.04064939#0.070911999;0.040500991#0.070911999;0.040500991#0.070312001;0.04064939#0.070312001;0.04064939#0.070108801;0.03929779#0.070108801;0.03929779#0.070228191;0.0387477#0.070228191;0.0387477#0.0700278;0.0344551#0.0700278;0.0344551#0.070231;0.0356235#0.070231;0.0356235#0.074168;0.0361315#0.074168;0.0361315#0.074041;0.0385445#0.074041;0.0385445#0.0743204;0.0387477#0.0743204;0.0387477#0.0732536;0.0385445#0.0732536;0.0385445#0.073533;0.0361315#0.073533;0.0361315#0.072771;0.0385445#0.072771;0.0385445#0.0730504;0.0387477#0.0730504;0.0387477#0.0719836;0.0385445#0.0719836;0.0385445#0.072263;0.0361315#0.072263;0.0361315#0.071501')
		pointStrings.append('0.0344551#0.0762762;0.0387477#0.0762762;0.0387477#0.076075809;0.048654691#0.076075809;0.048718391#0.076118372;0.048895#0.076153503;0.048895#0.076153889;0.049364598#0.076116932;0.049822633#0.076006965;0.050257829#0.075826701;0.050659467#0.075580578;0.051017655#0.075274655;0.051323578#0.074916467;0.051569701#0.074514829;0.051749965#0.074079633;0.051859932#0.073621598;0.051896889#0.073152;0.051896503#0.073152;0.051861372#0.072975391;0.051818809#0.072911691;0.051818809#0.067042309;0.051861372#0.066978609;0.051910177#0.066523236;0.052017009#0.066084549;0.052217959#0.065680225;0.052500893#0.065327893;0.052853225#0.065044959;0.053257549#0.064844009;0.053696236#0.064737177;0.054151609#0.064688372;0.054215309#0.064645809;0.061608691#0.064645809;0.061672391#0.064688372;0.061849#0.064723503;0.061849#0.064723889;0.062318598#0.064686932;0.062776633#0.064576965;0.063211829#0.064396701;0.063613467#0.064150578;0.063971655#0.063844655;0.064277578#0.063486467;0.064523701#0.063084829;0.064703965#0.062649633;0.064813932#0.062191598;0.064850889#0.061722;0.064850503#0.061722;0.064815372#0.061545391;0.064772809#0.061481691;0.064772809#0.056501309;0.064815372#0.056437609;0.064850503#0.056261;0.064850615#0.056261;0.064787074#0.055778363;0.064600783#0.055328617;0.064304438#0.05494241;0.063918231#0.054646066;0.063468485#0.054459775;0.062985848#0.054396234;0.062985848#0.054396345;0.062809239#0.054431476;0.062745539#0.054474039;0.061698861#0.054474039;0.061698861#0.053689448;0.061495661#0.053689448;0.061495661#0.053968848;0.059082661#0.053968848;0.059082661#0.053841848;0.058574661#0.053841848;0.058574661#0.055238848;0.057406261#0.055238848;0.057406261#0.055442048;0.061698861#0.055442048;0.061698861#0.055241657;0.062745539#0.055241657;0.062809239#0.05528422;0.062985848#0.055319351;0.062990072#0.055315648;0.063230669#0.055347321;0.063458801#0.05544182;0.063654706#0.055592142;0.063805029#0.055788047;0.063899527#0.05601618;0.063931201#0.056256776;0.063927497#0.056261;0.063962628#0.056437609;0.064005191#0.056501309;0.064005191#0.061481691;0.063962628#0.061545391;0.063913823#0.062000764;0.063806991#0.062439451;0.063606041#0.062843775;0.063323107#0.063196107;0.062970775#0.063479041;0.062566451#0.063679991;0.062127764#0.063786823;0.061672391#0.063835628;0.061608691#0.063878191;0.054215309#0.063878191;0.054151609#0.063835628;0.053975#0.063800497;0.053975#0.063800111;0.053505402#0.063837068;0.053047367#0.063947035;0.052612171#0.064127299;0.052210533#0.064373422;0.051852345#0.064679345;0.051546422#0.065037533;0.051300299#0.065439171;0.051120035#0.065874367;0.051010068#0.066332402;0.050973111#0.066802;0.050973497#0.066802;0.051008628#0.066978609;0.051051191#0.067042309;0.051051191#0.072911691;0.051008628#0.072975391;0.050959269#0.073430484;0.050852059#0.073869053;0.05065158#0.074273583;0.050369107#0.074626107;0.050016793#0.074909015;0.049611657#0.075109249;0.049173019#0.075217995;0.048718391#0.075265628;0.048654691#0.075308191;0.0387477#0.075308191;0.0387477#0.0745236;0.0385445#0.0745236;0.0385445#0.074803;0.0361315#0.074803;0.0361315#0.074676;0.0356235#0.074676;0.0356235#0.076073;0.0344551#0.076073')
		pointStrings.append('0.04085259#0.070312001;0.04100099#0.070312001;0.04100099#0.0705104;0.04120419#0.0705104;0.04120419#0.070108801;0.04085259#0.070108801')
		pointStrings.append('0.04085259#0.071115199;0.04120419#0.071115199;0.04120419#0.0707136;0.04100099#0.0707136;0.04100099#0.070911999;0.04085259#0.070911999')
		pointStrings.append('0.048103495#0.048488765;0.048280791#0.048141167;0.048628391#0.047963874;0.048628391#0.047758309;0.048133356#0.047993731;0.047897931#0.048488765')
		pointStrings.append('0.048019519#0.049046227;0.048274702#0.049299388;0.048628391#0.049422426;0.048628391#0.049216862;0.048386583#0.049123551;0.04819446#0.048932951;0.048103495#0.048691965;0.047897931#0.048691965')
		pointStrings.append('0.048103495#0.051028765;0.048194461#0.050787782;0.048386585#0.050597184;0.048628391#0.050503874;0.048628391#0.050298309;0.048274704#0.050421347;0.048019521#0.050674504;0.047897931#0.051028765')
		pointStrings.append('0.048133354#0.051727003;0.048628391#0.051962426;0.048628391#0.051756862;0.048280789#0.051579567;0.048103495#0.051231965;0.047897931#0.051231965')
		pointStrings.append('0.048831591#0.047963874;0.049072573#0.048054839;0.049263172#0.048246961;0.049356483#0.048488765;0.049562047#0.048488765;0.049439008#0.048135079;0.04918585#0.047879899;0.048831591#0.047758309')
		pointStrings.append('0.049183364#0.050079181;0.049267821#0.050283085;0.049348746#0.050388545;0.049258167#0.050479124;0.049152706#0.0503982;0.048948802#0.050313742;0.048831591#0.050298309;0.048831591#0.050503874;0.049076314#0.050598433;0.049261923#0.050784042;0.049356483#0.051028765;0.049562047#0.051028765;0.049546614#0.050911554;0.049462157#0.050707651;0.049381232#0.05060219;0.049471811#0.050511611;0.049577272#0.050592535;0.049781176#0.050676993;0.049999989#0.050705802;0.050218802#0.050676993;0.050422706#0.050592535;0.050528167#0.050511611;0.050618746#0.05060219;0.050537821#0.050707651;0.050453364#0.050911554;0.050437931#0.051028768;0.050643495#0.051028768;0.050738227#0.050784533;0.050924058#0.050599606;0.051168591#0.050505083;0.051359375#0.050502864;0.051613788#0.05059653;0.051806291#0.050787428;0.051896483#0.051028768;0.052102047#0.051028768;0.052046724#0.05079654;0.051921852#0.050592006;0.051744606#0.050430727;0.051527855#0.050329917;0.051553115#0.050202917;0.052910461#0.050202917;0.052910461#0.050946248;0.053113661#0.050946248;0.053113661#0.050666848;0.055526661#0.050666848;0.055526661#0.050793848;0.056034661#0.050793848;0.056034661#0.049396848;0.057203061#0.049396848;0.057203061#0.049193648;0.052910461#0.049193648;0.052910461#0.049435299;0.051745878#0.049435299;0.051711261#0.049308299;0.051905432#0.049148016;0.052041637#0.048935793;0.052102047#0.048691965;0.051896483#0.048691965;0.051806291#0.048933308;0.051613787#0.049124206;0.051359372#0.049217873;0.051168588#0.049215653;0.050924056#0.049121128;0.050738226#0.0489362;0.050643495#0.048691965;0.050437931#0.048691965;0.050453364#0.048809181;0.050537821#0.049013085;0.050618746#0.049118545;0.050528167#0.049209124;0.050422706#0.0491282;0.050218802#0.049043742;0.049999989#0.049014934;0.049781176#0.049043742;0.049577272#0.0491282;0.049471811#0.049209124;0.049381232#0.049118545;0.049462157#0.049013085;0.049546614#0.048809181;0.049562047#0.048691965;0.049356483#0.048691965;0.049261925#0.048936691;0.049076316#0.049122302;0.048831591#0.049216862;0.048831591#0.049422426;0.048948802#0.049406993;0.049152706#0.049322535;0.049258167#0.049241611;0.049348746#0.04933219;0.049267821#0.049437651;0.049183364#0.049641554;0.049154555#0.049860368')
		pointStrings.append('0.048831591#0.051962426;0.049185852#0.051840836;0.04943901#0.051585653;0.049562047#0.051231965;0.049356483#0.051231965;0.049263173#0.051473772;0.049072574#0.051665896;0.048831591#0.051756862')
		pointStrings.append('0.0646176#0.026416;0.065786#0.026416;0.065786#0.027813;0.066294#0.027813;0.066294#0.027686;0.068707#0.027686;0.068707#0.0279654;0.0689102#0.0279654;0.0689102#0.027508203;0.068961003#0.027260111;0.069117812#0.027256488;0.071177051#0.026438277;0.072294022#0.024524561;0.07235938#0.02386173;0.072358021#0.02386173;0.072321598#0.023306016;0.072212952#0.022759812;0.07203394#0.022232463;0.071787626#0.021732989;0.071478226#0.02126994;0.071111034#0.020851236;0.07069233#0.020484043;0.07022928#0.020174643;0.069729807#0.019928329;0.069202457#0.019749318;0.068656253#0.019640672;0.068100539#0.019604248;0.068100539#0.019604497;0.067923931#0.019639628;0.06786023#0.019682191;0.054010405#0.019682191;0.053946704#0.019639628;0.053252146#0.019569254;0.052582254#0.019391374;0.051964895#0.019076311;0.051426054#0.018639947;0.05098969#0.018101106;0.050674628#0.017483747;0.050496747#0.016813855;0.050426374#0.016119297;0.050383811#0.016055597;0.050383811#0.012145129;0.050498672#0.011934455;0.050498672#0.011693159;0.050383811#0.011482484;0.050383811#0.011380323;0.050425418#0.011332349;0.05049009#0.01119404;0.050490349#0.010904277;0.050275661#0.010617775;0.049925773#0.010541927;0.049611717#0.010713808;0.049573266#0.010764293;0.049487009#0.011049119;0.049573709#0.011333809;0.049616192#0.011380323;0.049616192#0.011482484;0.049501332#0.011693159;0.049501332#0.011934454;0.049616192#0.012145129;0.049616192#0.016055597;0.04957363#0.016119297;0.049538499#0.016295906;0.049538306#0.016295906;0.049574508#0.016848265;0.049682502#0.017391174;0.049860431#0.017915341;0.050105259#0.0184118;0.050412792#0.018872055;0.050777767#0.019288234;0.051193946#0.019653209;0.051654202#0.019960742;0.05215066#0.02020557;0.052674827#0.0203835;0.053217737#0.020491493;0.053770096#0.020527696;0.053770096#0.020527503;0.053946704#0.020492372;0.054010405#0.020449809;0.06786023#0.020449809;0.067923931#0.020492372;0.068623497#0.020563148;0.069298221#0.020742487;0.069920023#0.021059938;0.070462765#0.021499505;0.070803216#0.02189812;0.071077117#0.022345089;0.071277726#0.022829401;0.071400101#0.02333913;0.0714394#0.023838446;0.071395196#0.024345923;0.070578696#0.025742615;0.069075203#0.026332368;0.068948201#0.026217413;0.068948201#0.0262128;0.066128801#0.0262128;0.066128801#0.027294164;0.066064445#0.027349889;0.0659892#0.027321502;0.0659892#0.0262128;0.0646176#0.0262128')
		pointStrings.append('0.050643495#0.048488765;0.050736816#0.04824681;0.050927309#0.048054712;0.051168391#0.047963874;0.051168391#0.047758309;0.050814059#0.047879695;0.050560855#0.048135034;0.050437931#0.048488765')
		pointStrings.append('0.050560856#0.0515857;0.050814061#0.05184104;0.051168394#0.051962426;0.051168394#0.051756863;0.050927309#0.051666025;0.050736816#0.051473925;0.050643495#0.051231968;0.050437931#0.051231968')
		pointStrings.append('0.050809601#0.054535535;0.050809601#0.054332335;0.050458002#0.054332335;0.050458002#0.054733934;0.050661202#0.054733934;0.050661202#0.054535535')
		pointStrings.append('0.050458002#0.055338734;0.050809601#0.055338734;0.050809601#0.055135534;0.050661202#0.055135534;0.050661202#0.054937134;0.050458002#0.054937134')
		pointStrings.append('0.051012801#0.055338734;0.052364401#0.055338734;0.052364401#0.055241657;0.052910461#0.055241657;0.052910461#0.055442048;0.057203061#0.055442048;0.057203061#0.055238848;0.056034661#0.055238848;0.056034661#0.053841848;0.055526661#0.053841848;0.055526661#0.053968848;0.053113661#0.053968848;0.053113661#0.053689448;0.052910461#0.053689448;0.052910461#0.054474039;0.052364401#0.054474039;0.052364401#0.054332335;0.051012801#0.054332335;0.051012801#0.054535535;0.051161201#0.054535535;0.051161201#0.055135534;0.051012801#0.055135534')
		pointStrings.append('0.051371591#0.047963874;0.051718797#0.048140753;0.051896483#0.048488765;0.052102047#0.048488765;0.051866548#0.047993627;0.051371591#0.047758309')
		pointStrings.append('0.051371594#0.051962423;0.051866551#0.051727106;0.052102047#0.051231968;0.051896483#0.051231968;0.0517188#0.051579981;0.051371594#0.051756861')
		pointStrings.append('0.055526661#0.051936848;0.055526661#0.052063848;0.056034661#0.052063848;0.056034661#0.051301848;0.055526661#0.051301848;0.055526661#0.051428848;0.053113661#0.051428848;0.053113661#0.051149448;0.052910461#0.051149448;0.052910461#0.052216248;0.053113661#0.052216248;0.053113661#0.051936848')
		pointStrings.append('0.055526661#0.053206848;0.055526661#0.053333848;0.056034661#0.053333848;0.056034661#0.052571848;0.055526661#0.052571848;0.055526661#0.052698848;0.053113661#0.052698848;0.053113661#0.052419448;0.052910461#0.052419448;0.052910461#0.053486248;0.053113661#0.053486248;0.053113661#0.053206848')
		pointStrings.append('0.057818401#0.031577001;0.057818401#0.031373801;0.057466802#0.031373801;0.057466802#0.0317754;0.057670002#0.0317754;0.057670002#0.031577001')
		pointStrings.append('0.057466802#0.032380199;0.057818401#0.032380199;0.057818401#0.032176999;0.057670002#0.032176999;0.057670002#0.0319786;0.057466802#0.0319786')
		pointStrings.append('0.058021601#0.032380199;0.059373201#0.032380199;0.059373201#0.032260809;0.0601218#0.032260809;0.0601218#0.0324612;0.0644144#0.0324612;0.0644144#0.032258;0.063246#0.032258;0.063246#0.030861;0.062738#0.030861;0.062738#0.030988;0.060325#0.030988;0.060325#0.0307086;0.0601218#0.0307086;0.0601218#0.031493191;0.059373201#0.031493191;0.059373201#0.031373801;0.058021601#0.031373801;0.058021601#0.031577001;0.058170001#0.031577001;0.058170001#0.032176999;0.058021601#0.032176999')
		pointStrings.append('0.061495661#0.051936848;0.061495661#0.052216248;0.061698861#0.052216248;0.061698861#0.051149448;0.061495661#0.051149448;0.061495661#0.051428848;0.059082661#0.051428848;0.059082661#0.051301848;0.058574661#0.051301848;0.058574661#0.052063848;0.059082661#0.052063848;0.059082661#0.051936848')
		pointStrings.append('0.061495661#0.053206848;0.061495661#0.053486248;0.061698861#0.053486248;0.061698861#0.052419448;0.061495661#0.052419448;0.061495661#0.052698848;0.059082661#0.052698848;0.059082661#0.052571848;0.058574661#0.052571848;0.058574661#0.053333848;0.059082661#0.053333848;0.059082661#0.053206848')
		pointStrings.append('0.062738#0.028956;0.062738#0.029083;0.063246#0.029083;0.063246#0.028321;0.062738#0.028321;0.062738#0.028448;0.060325#0.028448;0.060325#0.0281686;0.0601218#0.0281686;0.0601218#0.0292354;0.060325#0.0292354;0.060325#0.028956')
		pointStrings.append('0.062738#0.030226;0.062738#0.030353;0.063246#0.030353;0.063246#0.029591;0.062738#0.029591;0.062738#0.029718;0.060325#0.029718;0.060325#0.0294386;0.0601218#0.0294386;0.0601218#0.0305054;0.060325#0.0305054;0.060325#0.030226')
		pointStrings.append('0.0646176#0.0324612;0.0659892#0.0324612;0.0659892#0.031352493;0.066064442#0.031324111;0.066128798#0.031379836;0.066128801#0.0324612;0.068948201#0.0324612;0.068948201#0.032260809;0.081166691#0.032260809;0.081230391#0.032303372;0.081735762#0.032366512;0.082207827#0.032533993;0.082610396#0.032832604;0.082822044#0.033090498;0.082979313#0.033384726;0.083076158#0.033703984;0.083108432#0.034031659;0.083104497#0.034036;0.083139628#0.034212609;0.083182191#0.034276309;0.083182191#0.046876691;0.083139628#0.046940391;0.083104497#0.047117;0.083103484#0.047117;0.083142948#0.047618452;0.083260372#0.048107559;0.083452863#0.048572273;0.083715682#0.049001154;0.084042357#0.049383643;0.084424845#0.049710317;0.084853727#0.049973136;0.08531844#0.050165627;0.085807547#0.050283052;0.086308999#0.050322516;0.086308999#0.050321502;0.086485608#0.050286371;0.086549309#0.050243809;0.087542141#0.050243809;0.087752816#0.050358668;0.087994112#0.050358669;0.088204787#0.050243809;0.088314677#0.050243809;0.088361905#0.050285521;0.088645739#0.050371987;0.088929869#0.0502865;0.089131284#0.050025027;0.089131284#0.049694971;0.088929869#0.049433498;0.088645739#0.049348011;0.088361905#0.049434477;0.088314677#0.04947619;0.088204787#0.04947619;0.087994112#0.049361329;0.087752816#0.04936133;0.087542141#0.04947619;0.086549309#0.04947619;0.086485608#0.049433627;0.085990619#0.04938218;0.085513546#0.049263757;0.085073998#0.049043712;0.084690654#0.048735346;0.084382288#0.048352002;0.084162242#0.047912454;0.084043819#0.04743538;0.083992372#0.046940391;0.083949809#0.046876691;0.083949809#0.034276309;0.083992372#0.034212609;0.084027503#0.034036;0.084031272#0.034036;0.083980848#0.03352403;0.083831511#0.033031735;0.083589002#0.032578032;0.08326264#0.03218036;0.082864968#0.031853998;0.082411265#0.031611489;0.08191897#0.031462152;0.081407#0.031411728;0.081407#0.031415497;0.081230391#0.031450628;0.081166691#0.031493191;0.068948201#0.031493191;0.0689102#0.0307086;0.068707#0.0307086;0.068707#0.030988;0.066294#0.030988;0.066294#0.030861;0.065786#0.030861;0.065786#0.032258;0.0646176#0.032258')
		pointStrings.append('0.068707#0.028956;0.068707#0.0292354;0.0689102#0.0292354;0.0689102#0.0281686;0.068707#0.0281686;0.068707#0.028448;0.066294#0.028448;0.066294#0.028321;0.065786#0.028321;0.065786#0.029083;0.066294#0.029083;0.066294#0.028956')
		pointStrings.append('0.068707#0.030226;0.068707#0.0305054;0.0689102#0.0305054;0.0689102#0.0294386;0.068707#0.0294386;0.068707#0.029718;0.066294#0.029718;0.066294#0.029591;0.065786#0.029591;0.065786#0.030353;0.066294#0.030353;0.066294#0.030226')
		part = self._create_extrude(pointStrings, "(mask_bottom_layer_Zmax) - (mask_bottom_layer_Zmin)", up=False)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_bottom_layer_Zmax) - (0)"))
		part.setAttribute('LtdLayerNumber', 1010)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=160
		empro.toolkit.applyMaterial(part,self.materials["bottom_layer"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.032613501#0.070231;0.032613501#0.070993;0.030200501#0.070993;0.030200501#0.070861437;0.025341237#0.070861437;0.024602421#0.070796799;0.023886053#0.070604849;0.023321967#0.070351733;0.022800522#0.070019536;0.022332728#0.069615272;0.021928464#0.069147478;0.021596267#0.068626033;0.021343151#0.068061947;0.021151201#0.067345579;0.021086563#0.066606763;0.021086563#0.053502761;0.021035011#0.052913517;0.020881921#0.052342176;0.020680048#0.051892288;0.020415103#0.051476408;0.020092682#0.051103318;0.01963957#0.050723112;0.01912732#0.050427364;0.018666455#0.050251991;0.01818504#0.050145264;0.017693239#0.050109436;0.012347419#0.050109436;0.012181246#0.050159969;0.012014865#0.050109436;0.011596277#0.050109436;0.011429896#0.050159768;0.011263538#0.050109715;0.011145609#0.049956623;0.011145609#0.049763375;0.011263538#0.049610283;0.011429896#0.04956023;0.011596277#0.049610562;0.012014865#0.049610562;0.012181246#0.049560029;0.012347419#0.049610562;0.017693239#0.049610562;0.018369112#0.049669693;0.019024449#0.04984529;0.019540478#0.050076842;0.020017499#0.050380738;0.020445439#0.050750561;0.020881541#0.051270288;0.021220769#0.051857847;0.021421924#0.052386466;0.021544342#0.052938658;0.021585437#0.053502761;0.021585437#0.066606763;0.021642496#0.067258951;0.021811939#0.067891322;0.022035377#0.068389267;0.022328623#0.068849571;0.022685485#0.069262515;0.023098429#0.069619377;0.023558733#0.069912623;0.024056678#0.070136061;0.024689049#0.070305504;0.025341237#0.070362563;0.030200501#0.070362563;0.030200501#0.070231']
		part = self._create_extrude(pointStrings, "(mask_bottom_layer_Zmax) - (mask_bottom_layer_Zmin)", up=False)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_bottom_layer_Zmax) - (0)"))
		part.setAttribute('LtdLayerNumber', 1010)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=160
		empro.toolkit.applyMaterial(part,self.materials["bottom_layer"])
		assembly.append(part)
		self.addShortcut(5,part)
		pointStrings=['0.03075081#0.037116996;0.030983165#0.03655604;0.031352789#0.036074337;0.031834444#0.03570464;0.032395406#0.035472378;0.032997427#0.035393105;0.033599449#0.035472378;0.034160412#0.035704639;0.034642068#0.036074337;0.035011692#0.03655604;0.035244047#0.037116996;0.035323299#0.037718975;0.035323299#0.039795458;0.035385552#0.040268319;0.03556807#0.040708955;0.035858413#0.041087339;0.036236797#0.041377682;0.036677433#0.0415602;0.037150294#0.041622453;0.037623156#0.0415602;0.038063794#0.041377683;0.038442178#0.041087339;0.038732526#0.040708948;0.038915043#0.040268302;0.038977292#0.039795432;0.039012627#0.039391549;0.039117559#0.038999938;0.039341543#0.038545743;0.039658523#0.038150794;0.040140226#0.03778117;0.040701182#0.037548815;0.041303161#0.037469563;0.062409616#0.037469563;0.062916707#0.037506505;0.063413089#0.03761655;0.063888282#0.037797375;0.064416457#0.038102318;0.064883656#0.038494344;0.065275682#0.038961543;0.065580625#0.039489718;0.06576145#0.039964911;0.065871495#0.040461293;0.065908437#0.040968384;0.065908437#0.047237848;0.065866059#0.047722229;0.065740213#0.048191892;0.065471587#0.048736612;0.06509143#0.049210278;0.064617764#0.049590435;0.064073044#0.049859061;0.063603381#0.049984907;0.063119#0.050027285;0.061495661#0.050027285;0.061495661#0.050158848;0.059082661#0.050158848;0.059082661#0.049396848;0.061495661#0.049396848;0.061495661#0.049528411;0.063119#0.049528411;0.063516752#0.049493612;0.063902419#0.049390273;0.064349719#0.049169689;0.064738673#0.048857521;0.065050841#0.048468567;0.065271425#0.048021267;0.065374764#0.0476356;0.065409563#0.047237848;0.065409563#0.040968384;0.065363987#0.040447449;0.065228644#0.039942342;0.065050173#0.039544608;0.064815943#0.03917694;0.064530899#0.038847101;0.06420106#0.038562057;0.063833392#0.038327827;0.063435658#0.038149356;0.062930551#0.038014013;0.062409616#0.037968437;0.041303161#0.037968437;0.0408303#0.03803069;0.040389664#0.038213208;0.04001128#0.038503551;0.039720933#0.038881942;0.039538415#0.039322588;0.039396914#0.040397437;0.039164559#0.040958393;0.038794935#0.041440096;0.038313278#0.041809793;0.037752316#0.042042055;0.037150294#0.042121327;0.036548273#0.042042054;0.035987312#0.041809793;0.035505656#0.041440096;0.035136032#0.040958393;0.034903677#0.040397437;0.034824425#0.039795458;0.034824425#0.037718975;0.034762172#0.037246114;0.034579654#0.036805477;0.034289311#0.036427094;0.033910927#0.03613675;0.033470289#0.035954232;0.032997427#0.035891979;0.032524566#0.035954232;0.032083929#0.03613675;0.031705546#0.036427094;0.031415203#0.036805477;0.031232685#0.037246114;0.031170432#0.037718975;0.031170432#0.039795458;0.03109118#0.040397437;0.030858825#0.040958393;0.030489201#0.041440096;0.030007544#0.041809793;0.029446582#0.042042055;0.02884456#0.042121327;0.028242539#0.042042054;0.027681578#0.041809793;0.027199922#0.041440096;0.026830298#0.040958393;0.026597943#0.040397437;0.026456442#0.039322588;0.026273924#0.038881942;0.025983577#0.038503551;0.025605193#0.038213208;0.025164557#0.03803069;0.024691696#0.037968437;0.020179066#0.037968437;0.019565584#0.037932706;0.018960398#0.037825995;0.018371693#0.037649749;0.017671085#0.037335373;0.017023438#0.036922776;0.016442427#0.036420671;0.015940322#0.03583966;0.015527725#0.035192013;0.015213349#0.034491405;0.015037102#0.0339027;0.014930391#0.033297514;0.01489466#0.032684032;0.01489466#0.031771486;0.014934753#0.031125519;0.015054415#0.030489467;0.01525181#0.029873093;0.015523909#0.029285859;0.015866534#0.028736778;0.016274426#0.028234279;0.016741325#0.027786075;0.017260063#0.027399045;0.017822678#0.027079131;0.018558147#0.0267862;0.019329242#0.026607465;0.020118583#0.026547563;0.024758701#0.026547563;0.02536068#0.026626815;0.025921636#0.02685917;0.026403339#0.027228794;0.026710915#0.027609103;0.026932156#0.028045326;0.027057278#0.028518171;0.02708457#0.029006947;0.027146823#0.029479808;0.027329341#0.029920445;0.027619684#0.030298828;0.027998067#0.030589172;0.028438704#0.03077169;0.028911565#0.030833943;0.029384427#0.03077169;0.029825065#0.030589172;0.030203449#0.030298828;0.030493792#0.029920445;0.03067631#0.029479808;0.030738563#0.029006947;0.030738563#0.024173703;0.030817815#0.023571724;0.03105017#0.023010768;0.031419794#0.022529065;0.03190145#0.022159368;0.032462411#0.021927107;0.033064432#0.021847834;0.033666454#0.021927106;0.034227416#0.022159368;0.034709073#0.022529065;0.035078697#0.023010768;0.035311052#0.023571724;0.035390304#0.024173703;0.035390304#0.028995883;0.035452557#0.029468744;0.035635075#0.02990938;0.035925418#0.030287764;0.036303802#0.030578107;0.036744438#0.030760625;0.037217299#0.030822878;0.037690161#0.030760625;0.038130799#0.030578108;0.038509183#0.030287764;0.038799526#0.02990938;0.038982044#0.029468744;0.039044297#0.028995883;0.039072867#0.028509998;0.039198681#0.028040175;0.039419452#0.027606789;0.039725528#0.027228794;0.040207231#0.02685917;0.040768187#0.026626815;0.041370166#0.026547563;0.060325#0.026547563;0.060325#0.026416;0.062738#0.026416;0.062738#0.027178;0.060325#0.027178;0.060325#0.027046437;0.041370166#0.027046437;0.040897305#0.02710869;0.040456669#0.027291208;0.040078285#0.027581551;0.039787942#0.027959935;0.039605424#0.028400571;0.039543171#0.028873432;0.039514601#0.029359317;0.039388787#0.029829141;0.039168016#0.030262526;0.03886194#0.030640521;0.038380283#0.031010218;0.037819321#0.03124248;0.037217299#0.031321752;0.036615278#0.031242479;0.036054317#0.031010218;0.035572661#0.030640521;0.035203037#0.030158818;0.034970682#0.029597862;0.03489143#0.028995883;0.03489143#0.024173703;0.034829177#0.023700842;0.034646659#0.023260206;0.034356316#0.022881822;0.033977932#0.022591478;0.033537294#0.022408961;0.033064432#0.022346708;0.032591571#0.022408961;0.032150935#0.022591479;0.031772551#0.022881822;0.031482208#0.023260206;0.03129969#0.023700842;0.031237437#0.024173703;0.031237437#0.029006947;0.031158185#0.029608926;0.03092583#0.030169882;0.030556206#0.030651585;0.03007455#0.031021283;0.029513587#0.031253544;0.028911565#0.031332817;0.028309544#0.031253544;0.027748582#0.031021282;0.027266927#0.030651585;0.026959351#0.030271276;0.02673811#0.029835053;0.026612988#0.029362208;0.026585696#0.028873432;0.026523443#0.028400571;0.026340925#0.027959935;0.026050582#0.027581551;0.025672198#0.027291208;0.025231562#0.02710869;0.024758701#0.027046437;0.020118583#0.027046437;0.019404839#0.027100655;0.018707475#0.027262066;0.018042495#0.027526965;0.017533512#0.027816299;0.017064217#0.028166358;0.016641818#0.028571768;0.016272798#0.029026303;0.015962823#0.029522986;0.015716653#0.030054191;0.015538067#0.030611762;0.015429806#0.031187138;0.015393534#0.031771486;0.015393534#0.032684032;0.015444061#0.033377608;0.015594577#0.034056538;0.015841901#0.034706485;0.01610602#0.035196324;0.01642522#0.035652188;0.016795184#0.036067914;0.01721091#0.036437878;0.017666774#0.036757078;0.018156613#0.037021196;0.01880656#0.03726852;0.01948549#0.037419036;0.020179066#0.037469563;0.024691696#0.037469563;0.025293675#0.037548815;0.025854631#0.03778117;0.026336334#0.038150794;0.026653314#0.038545743;0.026877298#0.038999938;0.02698223#0.039391549;0.027017565#0.039795432;0.027079814#0.040268302;0.027262331#0.040708948;0.027552679#0.041087339;0.027931063#0.041377682;0.028371699#0.0415602;0.02884456#0.041622453;0.029317422#0.0415602;0.02975806#0.041377683;0.030136444#0.041087339;0.030426787#0.040708955;0.030609305#0.040268319;0.030671558#0.039795458;0.030671558#0.037718975']
		part = self._create_extrude(pointStrings, "(mask_bottom_layer_Zmax) - (mask_bottom_layer_Zmin)", up=False)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_bottom_layer_Zmax) - (0)"))
		part.setAttribute('LtdLayerNumber', 1010)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=160
		empro.toolkit.applyMaterial(part,self.materials["bottom_layer"])
		assembly.append(part)
		self.addShortcut(4,part)
		pointStrings=['0.032613501#0.075311;0.032613501#0.076073;0.030200501#0.076073;0.030200501#0.075941437;0.02924986#0.075941437;0.029113815#0.075945754;0.027466373#0.076600461;0.026574114#0.078132316;0.026521749#0.078663099;0.026552159#0.07907986;0.026642646#0.079487815;0.026791298#0.07987835;0.027041958#0.080312424;0.027364181#0.08069638;0.027680363#0.080969591;0.0280328#0.081194097;0.028414052#0.081365157;0.028898226#0.08149488;0.029397569#0.081538563;0.045458057#0.081538563;0.04615248#0.081589152;0.04683224#0.081739851;0.047482981#0.081987478;0.047973419#0.082251919;0.04842984#0.082571509;0.048846074#0.082941925;0.04921649#0.083358159;0.04953608#0.08381458;0.049800521#0.084305018;0.050048148#0.084955759;0.050198847#0.085635519;0.050249436#0.086329942;0.050249436#0.087750459;0.050296661#0.087871815;0.050287494#0.088001817;0.050249436#0.088083013;0.050249436#0.088479723;0.050287227#0.088560999;0.050287564#0.088731101;0.05016962#0.088893748;0.04997546#0.088945387;0.049792299#0.088862824;0.04970192#0.088678903;0.049750562#0.088479723;0.049750562#0.088083013;0.049700026#0.087916649;0.049750562#0.087750459;0.049750562#0.086329942;0.04970524#0.085707821;0.049570231#0.085098838;0.049348388#0.084515851;0.049111479#0.084076478;0.048825165#0.083667578;0.048493316#0.083294683;0.048120421#0.082962834;0.047711521#0.08267652;0.047272148#0.082439611;0.046689161#0.082217768;0.046080178#0.082082759;0.045458057#0.082037437;0.029397569#0.082037437;0.02881157#0.081986313;0.028243438#0.081833949;0.027796049#0.081633214;0.027382473#0.081369763;0.027011443#0.081049156;0.026633323#0.080598592;0.026339181#0.080089218;0.026164742#0.079630935;0.02605856#0.079152211;0.026022875#0.078663152;0.02608471#0.078035714;0.027140898#0.076222421;0.029091014#0.075447428;0.029250132#0.075442563;0.030200501#0.075442563;0.030200501#0.075311']
		part = self._create_extrude(pointStrings, "(mask_bottom_layer_Zmax) - (mask_bottom_layer_Zmin)", up=False)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_bottom_layer_Zmax) - (0)"))
		part.setAttribute('LtdLayerNumber', 1010)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=160
		empro.toolkit.applyMaterial(part,self.materials["bottom_layer"])
		assembly.append(part)
		self.addShortcut(3,part)
		pointStrings=['0.0385445#0.070231;0.0385445#0.070362563;0.03950099#0.070362563;0.03950099#0.070312001;0.040000989#0.070312001;0.040000989#0.070911999;0.03950099#0.070911999;0.03950099#0.070861437;0.0385445#0.070861437;0.0385445#0.070993;0.0361315#0.070993;0.0361315#0.070231']
		part = self._create_extrude(pointStrings, "(mask_bottom_layer_Zmax) - (mask_bottom_layer_Zmin)", up=False)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_bottom_layer_Zmax) - (0)"))
		part.setAttribute('LtdLayerNumber', 1010)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=160
		empro.toolkit.applyMaterial(part,self.materials["bottom_layer"])
		assembly.append(part)
		self.addShortcut(9,part)
		self._update_geoProgress()
		pointStrings=['0.061495661#0.054476848;0.061495661#0.054608411;0.062985848#0.054608411;0.06341357#0.054664722;0.063812143#0.054829816;0.064154405#0.055092443;0.064417032#0.055434705;0.064582126#0.055833278;0.064638437#0.056261;0.064638437#0.061722;0.064596059#0.062206381;0.064470213#0.062676044;0.064201587#0.063220764;0.06382143#0.06369443;0.063347764#0.064074587;0.062803044#0.064343213;0.062333381#0.064469059;0.061849#0.064511437;0.053975#0.064511437;0.053577248#0.064546236;0.053191581#0.064649575;0.052744281#0.064870159;0.052355327#0.065182327;0.052043159#0.065571281;0.051822575#0.066018581;0.051719236#0.066404248;0.051684437#0.066802;0.051684437#0.073152;0.051642059#0.073636381;0.051516213#0.074106044;0.051247587#0.074650764;0.05086743#0.07512443;0.050393764#0.075504587;0.049849044#0.075773213;0.049379381#0.075899059;0.048895#0.075941437;0.0385445#0.075941437;0.0385445#0.076073;0.0361315#0.076073;0.0361315#0.075311;0.0385445#0.075311;0.0385445#0.075442563;0.048895#0.075442563;0.049292752#0.075407764;0.049678419#0.075304425;0.050125719#0.075083841;0.050514673#0.074771673;0.050826841#0.074382719;0.051047425#0.073935419;0.051150764#0.073549752;0.051185563#0.073152;0.051185563#0.066802;0.051227941#0.066317619;0.051353787#0.065847956;0.051622413#0.065303237;0.05200257#0.06482957;0.052476237#0.064449413;0.053020956#0.064180787;0.053490619#0.064054941;0.053975#0.064012563;0.061849#0.064012563;0.062246752#0.063977764;0.062632419#0.063874425;0.063079719#0.063653841;0.063468673#0.063341673;0.063780841#0.062952719;0.064001425#0.062505419;0.064104764#0.062119752;0.064139563#0.061722;0.064139563#0.056261;0.064100251#0.055962397;0.063984994#0.055684143;0.063801648#0.0554452;0.063562705#0.055261854;0.063284451#0.055146597;0.062985848#0.055107285;0.061495661#0.055107285;0.061495661#0.055238848;0.059082661#0.055238848;0.059082661#0.054476848']
		part = self._create_extrude(pointStrings, "(mask_bottom_layer_Zmax) - (mask_bottom_layer_Zmin)", up=False)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_bottom_layer_Zmax) - (0)"))
		part.setAttribute('LtdLayerNumber', 1010)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=160
		empro.toolkit.applyMaterial(part,self.materials["bottom_layer"])
		assembly.append(part)
		self.addShortcut(1,part)
		pointStrings=['0.055526661#0.049396848;0.055526661#0.050158848;0.053113661#0.050158848;0.053113661#0.050068545;0.050599534#0.050068545;0.050499616#0.050252284;0.050345145#0.050393371;0.050153211#0.050476605;0.049944645#0.050492952;0.049731626#0.050435873;0.049550976#0.050309381;0.049424484#0.050128731;0.049367405#0.049915712;0.049386626#0.049696018;0.049479827#0.049496147;0.049635768#0.049340206;0.049835639#0.049247005;0.050049058#0.049227267;0.050256887#0.049279654;0.050435448#0.049398199;0.050563868#0.049569671;0.053113661#0.049569671;0.053113661#0.049396848']
		part = self._create_extrude(pointStrings, "(mask_bottom_layer_Zmax) - (mask_bottom_layer_Zmin)", up=False)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_bottom_layer_Zmax) - (0)"))
		part.setAttribute('LtdLayerNumber', 1010)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=160
		empro.toolkit.applyMaterial(part,self.materials["bottom_layer"])
		assembly.append(part)
		self.addShortcut(6,part)
		pointStrings=['0.049749701#0.010882146;0.04977222#0.01085258;0.049956146#0.010751918;0.050161057#0.010796338;0.050286789#0.010964127;0.050286637#0.011133826;0.050249439#0.011215277;0.050249439#0.01164753;0.050294258#0.011755387;0.050294258#0.011872227;0.050249439#0.011980084;0.050249439#0.016295906;0.050286611#0.016806161;0.050397343#0.017305642;0.050579297#0.0177838;0.050886143#0.018315272;0.051280616#0.018785386;0.05175073#0.019179859;0.052282202#0.019486705;0.05276036#0.019668659;0.053259841#0.019779391;0.053770096#0.019816563;0.068100539#0.019816563;0.068686813#0.019859273;0.069260706#0.019986502;0.069810101#0.020195563;0.070420752#0.020548123;0.070960905#0.021001365;0.071414146#0.021541518;0.071766706#0.022152168;0.071975767#0.022701563;0.072102997#0.023275456;0.072145707#0.02386173;0.072084804#0.02448298;0.071037953#0.026276559;0.069107987#0.027043404;0.068961022#0.027046784;0.068745001#0.027046437;0.068745001#0.027178;0.066332001#0.027178;0.066332001#0.026416;0.068745001#0.026416;0.068745001#0.026547563;0.068961067#0.026547978;0.069085013#0.026545128;0.070712686#0.025898394;0.071595566#0.024385746;0.071646833#0.02386173;0.07160939#0.023347759;0.071497852#0.022844642;0.071314573#0.022363002;0.071005493#0.02182766;0.070608147#0.021354122;0.070218239#0.021017166;0.069783611#0.020740278;0.069313443#0.020529304;0.068716346#0.020369313;0.068100539#0.020315437;0.053770096#0.020315437;0.053072112#0.020254371;0.052395335#0.02007303;0.051862425#0.019833902;0.051369799#0.019520065;0.050927858#0.019138144;0.050545937#0.018696204;0.050232099#0.018203577;0.049992972#0.017670667;0.049811631#0.01699389;0.049750565#0.016295906;0.049750565#0.011980084;0.049705746#0.011872227;0.049705746#0.011755387;0.049750565#0.01164753;0.049750565#0.011215277;0.049699185#0.011048953']
		part = self._create_extrude(pointStrings, "(mask_bottom_layer_Zmax) - (mask_bottom_layer_Zmin)", up=False)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_bottom_layer_Zmax) - (0)"))
		part.setAttribute('LtdLayerNumber', 1010)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=160
		empro.toolkit.applyMaterial(part,self.materials["bottom_layer"])
		assembly.append(part)
		self.addShortcut(7,part)
		pointStrings=['0.052161201#0.054535535;0.052161201#0.054608411;0.053113661#0.054608411;0.053113661#0.054476848;0.055526661#0.054476848;0.055526661#0.055238848;0.053113661#0.055238848;0.053113661#0.055107285;0.052161201#0.055107285;0.052161201#0.055135534;0.051661202#0.055135534;0.051661202#0.054535535']
		part = self._create_extrude(pointStrings, "(mask_bottom_layer_Zmax) - (mask_bottom_layer_Zmin)", up=False)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_bottom_layer_Zmax) - (0)"))
		part.setAttribute('LtdLayerNumber', 1010)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=160
		empro.toolkit.applyMaterial(part,self.materials["bottom_layer"])
		assembly.append(part)
		self.addShortcut(8,part)
		pointStrings=['0.059170001#0.031577001;0.059170001#0.031627563;0.060325#0.031627563;0.060325#0.031496;0.062738#0.031496;0.062738#0.032258;0.060325#0.032258;0.060325#0.032126437;0.059170001#0.032126437;0.059170001#0.032176999;0.058670002#0.032176999;0.058670002#0.031577001']
		part = self._create_extrude(pointStrings, "(mask_bottom_layer_Zmax) - (mask_bottom_layer_Zmin)", up=False)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_bottom_layer_Zmax) - (0)"))
		part.setAttribute('LtdLayerNumber', 1010)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=160
		empro.toolkit.applyMaterial(part,self.materials["bottom_layer"])
		assembly.append(part)
		self.addShortcut(10,part)
		self._update_geoProgress()
		pointStrings=['0.068745001#0.031496;0.068745001#0.031627563;0.081407#0.031627563;0.081928281#0.031684653;0.082424849#0.031853215;0.082788423#0.032063124;0.083110022#0.032332978;0.083379876#0.032654577;0.083589785#0.033018151;0.083758347#0.033514719;0.083815437#0.034036;0.083815437#0.047117;0.083874545#0.047656706;0.084049064#0.048170825;0.084266393#0.048547248;0.084545784#0.048880215;0.084878751#0.049159606;0.085255174#0.049376935;0.085769293#0.049551454;0.086308999#0.049610562;0.087707187#0.049610562;0.08787336#0.049560029;0.088039741#0.049610562;0.088479723#0.049610562;0.088646104#0.04956023;0.088812462#0.049610283;0.088930391#0.049763375;0.088930391#0.049956623;0.088812462#0.050109715;0.088646104#0.050159768;0.088479723#0.050109436;0.088039741#0.050109436;0.08787336#0.050159969;0.087707187#0.050109436;0.086308999#0.050109436;0.085661317#0.050038503;0.085044341#0.049829068;0.084592608#0.04956826;0.084193027#0.049232972;0.083857739#0.048833391;0.083596931#0.048381658;0.083387496#0.047764682;0.083316563#0.047117;0.083316563#0.034036;0.083251496#0.033541769;0.08306073#0.033081219;0.082757265#0.032685735;0.082361781#0.03238227;0.081901231#0.032191504;0.081407#0.032126437;0.068745001#0.032126437;0.068745001#0.032258;0.066332001#0.032258;0.066332001#0.031496']
		part = self._create_extrude(pointStrings, "(mask_bottom_layer_Zmax) - (mask_bottom_layer_Zmin)", up=False)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_bottom_layer_Zmax) - (0)"))
		part.setAttribute('LtdLayerNumber', 1010)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=160
		empro.toolkit.applyMaterial(part,self.materials["bottom_layer"])
		assembly.append(part)
		self.addShortcut(2,part)
		self._setAssemblyMeshSettings(assembly,0,0,0)
		assembly.name="bottom_layer"
		topAssembly.append(assembly)
		assembly=empro.geometry.Assembly()
		pointStrings=['0.011371976#0.049721416;0.011486782#0.049721416;0.011567962#0.049802596;0.011567962#0.049917402;0.011486782#0.049998582;0.011371976#0.049998582;0.011290796#0.049917402;0.011290796#0.049802596']
		part = self._create_extrude(pointStrings, "(mask_drill_plated_bottom_top_Zmax) - (mask_drill_plated_bottom_top_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_drill_plated_bottom_top_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 1014)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["drill_plated_bottom_top"])
		assembly.append(part)
		self.addShortcut(5,part)
		pointStrings=['0.01212436#0.049721416;0.012239166#0.049721416;0.012320346#0.049802596;0.012320346#0.049917402;0.012239166#0.049998582;0.01212436#0.049998582;0.01204318#0.049917402;0.01204318#0.049802596']
		part = self._create_extrude(pointStrings, "(mask_drill_plated_bottom_top_Zmax) - (mask_drill_plated_bottom_top_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_drill_plated_bottom_top_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 1014)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["drill_plated_bottom_top"])
		assembly.append(part)
		self.addShortcut(5,part)
		pointStrings=['0.048413165#0.048273543;0.048666242#0.048147597;0.048894693#0.048176027;0.049078278#0.048314933;0.049167745#0.048527051;0.049139368#0.048754795;0.049001164#0.048938022;0.04878998#0.049027879;0.048562125#0.049000408;0.04837835#0.048862933;0.048287654#0.048652109;0.048287217#0.048526619']
		part = self._create_extrude(pointStrings, "(mask_drill_plated_bottom_top_Zmax) - (mask_drill_plated_bottom_top_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_drill_plated_bottom_top_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 1014)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["drill_plated_bottom_top"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.048287655#0.051068624;0.048378352#0.050857802;0.048562126#0.050720329;0.04878998#0.050692858;0.049001162#0.050782714;0.049139367#0.050965939;0.049167745#0.051193681;0.049078281#0.051405801;0.048894695#0.05154471;0.048666242#0.05157314;0.048413164#0.051447193;0.048287217#0.051194114']
		part = self._create_extrude(pointStrings, "(mask_drill_plated_bottom_top_Zmax) - (mask_drill_plated_bottom_top_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_drill_plated_bottom_top_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 1014)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["drill_plated_bottom_top"])
		assembly.append(part)
		self.addShortcut(0,part)
		self._update_geoProgress()
		pointStrings=['0.049586894#0.049696256;0.04971427#0.049519861;0.049866326#0.049436441;0.05003873#0.049417559;0.050187843#0.049457514;0.050268099#0.049505779;0.050336236#0.04957;0.050364102#0.049605413;0.05037#0.049614671;0.050400439#0.049667442;0.050423064#0.04972403;0.050437736#0.049783181;0.050444489#0.049860368;0.050437736#0.049937555;0.050374803#0.050099158;0.050254944#0.050224481;0.05003873#0.050303177;0.049812135#0.050263222;0.049635876#0.050115323;0.049558494#0.049911971']
		part = self._create_extrude(pointStrings, "(mask_drill_plated_bottom_top_Zmax) - (mask_drill_plated_bottom_top_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_drill_plated_bottom_top_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 1014)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["drill_plated_bottom_top"])
		assembly.append(part)
		self.addShortcut(6,part)
		pointStrings=['0.049941673#0.010910136;0.050056479#0.010910136;0.05013766#0.010991317;0.05013766#0.011106123;0.050056479#0.011187304;0.049941673#0.011187304;0.049860492#0.011106123;0.049860492#0.010991317']
		part = self._create_extrude(pointStrings, "(mask_drill_plated_bottom_top_Zmax) - (mask_drill_plated_bottom_top_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_drill_plated_bottom_top_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 1014)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["drill_plated_bottom_top"])
		assembly.append(part)
		self.addShortcut(7,part)
		pointStrings=['0.049942543#0.088508037;0.050057349#0.088508037;0.050138529#0.088589217;0.050138529#0.088704023;0.050057349#0.088785203;0.049942543#0.088785203;0.049861363#0.088704023;0.049861363#0.088589217']
		part = self._create_extrude(pointStrings, "(mask_drill_plated_bottom_top_Zmax) - (mask_drill_plated_bottom_top_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_drill_plated_bottom_top_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 1014)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["drill_plated_bottom_top"])
		assembly.append(part)
		self.addShortcut(3,part)
		pointStrings=['0.049942546#0.087777634;0.05005735#0.087777634;0.05013853#0.087858814;0.05013853#0.087973618;0.05005735#0.088054798;0.049942546#0.088054798;0.049861366#0.087973618;0.049861366#0.087858814']
		part = self._create_extrude(pointStrings, "(mask_drill_plated_bottom_top_Zmax) - (mask_drill_plated_bottom_top_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_drill_plated_bottom_top_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 1014)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["drill_plated_bottom_top"])
		assembly.append(part)
		self.addShortcut(3,part)
		pointStrings=['0.049942599#0.011675225;0.050057405#0.011675225;0.050138584#0.011756404;0.050138584#0.01187121;0.050057405#0.011952389;0.049942599#0.011952389;0.04986142#0.01187121;0.04986142#0.011756404']
		part = self._create_extrude(pointStrings, "(mask_drill_plated_bottom_top_Zmax) - (mask_drill_plated_bottom_top_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_drill_plated_bottom_top_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 1014)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["drill_plated_bottom_top"])
		assembly.append(part)
		self.addShortcut(7,part)
		self._update_geoProgress()
		pointStrings=['0.050856054#0.048427871;0.050993566#0.048239341;0.051207635#0.048146456;0.05133339#0.048146227;0.051586269#0.048272721;0.051711689#0.048526134;0.051683652#0.048752273;0.051547236#0.048934799;0.051338297#0.049025737;0.051111753#0.049001185;0.050927148#0.048867596;0.050833004#0.048660082']
		part = self._create_extrude(pointStrings, "(mask_drill_plated_bottom_top_Zmax) - (mask_drill_plated_bottom_top_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_drill_plated_bottom_top_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 1014)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["drill_plated_bottom_top"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.05092715#0.05085314;0.051111754#0.050719552;0.051338297#0.050695;0.051547235#0.050785938;0.051683651#0.050968463;0.05171169#0.051194601;0.051586271#0.051448015;0.051333392#0.05157451;0.051207637#0.051574281;0.050993566#0.051481396;0.050856054#0.051292864;0.050833004#0.051060652']
		part = self._create_extrude(pointStrings, "(mask_drill_plated_bottom_top_Zmax) - (mask_drill_plated_bottom_top_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_drill_plated_bottom_top_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 1014)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["drill_plated_bottom_top"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.08781544#0.049721416;0.087930246#0.049721416;0.088011426#0.049802596;0.088011426#0.049917402;0.087930246#0.049998582;0.08781544#0.049998582;0.08773426#0.049917402;0.08773426#0.049802596']
		part = self._create_extrude(pointStrings, "(mask_drill_plated_bottom_top_Zmax) - (mask_drill_plated_bottom_top_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_drill_plated_bottom_top_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 1014)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["drill_plated_bottom_top"])
		assembly.append(part)
		self.addShortcut(2,part)
		pointStrings=['0.088589218#0.049721416;0.088704024#0.049721416;0.088785204#0.049802596;0.088785204#0.049917402;0.088704024#0.049998582;0.088589218#0.049998582;0.088508038#0.049917402;0.088508038#0.049802596']
		part = self._create_extrude(pointStrings, "(mask_drill_plated_bottom_top_Zmax) - (mask_drill_plated_bottom_top_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_drill_plated_bottom_top_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 1014)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["drill_plated_bottom_top"])
		assembly.append(part)
		self.addShortcut(2,part)
		self._setAssemblyMeshSettings(assembly,0,0,0)
		assembly.name="drill_plated_bottom_top"
		topAssembly.append(assembly)
		return symbPinData
		# End of create_geometry

	def _update_geoProgress(self):
		self.geoProgress+= 1
		if self.geoProgress % 1 == 0:
			progress = (self.geoProgress * 100)/6
			self._updateProgress(progress)

	def getMaskHeights(self,parameterized=False):
		mask_heights={}
		mask_heights_parameterized={}
		mask_heights[1010]=(0, 3.5001e-05)
		mask_heights_parameterized[1010]=("(mask_bottom_layer_Zmin) - (0)", "(mask_bottom_layer_Zmax) - (0)")
		mask_heights[1006]=(0.000701041, 0.000736042)
		mask_heights_parameterized[1006]=("(mask_top_layer_Zmin) - (0)", "(mask_top_layer_Zmax) - (0)")
		mask_heights[1014]=(3.5001e-05, 0.000701041)
		mask_heights_parameterized[1014]=("(mask_drill_plated_bottom_top_Zmin) - (0)", "(mask_drill_plated_bottom_top_Zmax) - (0)")
		if(parameterized):
			return mask_heights_parameterized
		else:
			return mask_heights

	def getMaskHeightsParameterized(self):
		return self.getMaskHeights(parameterized=True)

	def create_ports( self, topAssembly, includeInvalidPorts=True, symbPinData=None):
		self.setPortWarnings(includeInvalidPorts)
		V=empro.geometry.Vector3d
		L=empro.geometry.Line
		SPAresabs=empro.activeProject.newPartModelingUnit.toReferenceUnits(1e-6)
		if topAssembly != None:
			bbox_geom = topAssembly.boundingBox()
		else:
			bbox_geom = empro.activeProject.geometry.boundingBox()
		xLowerBoundary = float(bbox_geom.lower.x)
		xUpperBoundary = float(bbox_geom.upper.x)
		yLowerBoundary = float(bbox_geom.lower.y)
		yUpperBoundary = float(bbox_geom.upper.y)
		zLowerBoundary = float(bbox_geom.lower.z)
		zUpperBoundary = float(bbox_geom.upper.z)
		internalPortOnXLowerBoundary = False
		internalPortOnXUpperBoundary = False
		internalPortOnYLowerBoundary = False
		internalPortOnYUpperBoundary = False
		internalPortOnZLowerBoundary = False
		internalPortOnZUpperBoundary = False
		ports=[]
		waveguides={}
		portShortcutGroups=[]
		assembly=empro.geometry.Assembly()
		waveform=empro.waveform.Waveform("Broadband Pulse")
		waveform.shape=empro.waveform.MaximumFrequencyWaveformShape()
		self.waveforms["Broadband Pulse"]=waveform
		if getSessionVersion(self.session) >= 7:
			self.session.appendUniqueWaveforms(self.waveforms)
		else:
			for name,waveform in self.waveforms.items():
				empro.activeProject.waveforms.append(waveform)
				self.waveforms[name] = empro.activeProject.waveforms[len(empro.activeProject.waveforms)-1]
		feed=empro.components.Feed()
		feed.name="50 ohm Voltage Source"
		feed.impedance.resistance=50
		feed.waveform=self.waveforms["Broadband Pulse"]
		self.circuitComponentDefinitions[feed.name]=feed
		if getSessionVersion(self.session) >= 7:
			self.session.appendUniqueCircuitComponentDefinitions(self.circuitComponentDefinitions)
		else:
			for name,compDef in self.circuitComponentDefinitions.items():
				empro.activeProject.circuitComponentDefinitions.append(compDef)
				self.circuitComponentDefinitions[name] = empro.activeProject.circuitComponentDefinitions[len(empro.activeProject.circuitComponentDefinitions)-1]
		head=V("(0.050184995) - (0)","(0.049715184) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
		tail=V("(0.050184995) - (0)","(0.049715184) - (0)","(((mask_top_layer_Zmax) + (mask_top_layer_Zmin)) / (2)) - (0)")
		extent=empro.components.CylindricalExtent("0.00014373216","0.00014373216")
		port = self._create_internal_port("P1","50 ohm Voltage Source",head,tail,extent)
		portShortcutGroups.append((6,port))
		ports.append(port)
		self._set_extra_port_info(port, "inputOutput", 1, "P1", "Direct")
		headsAndTails = (head if isinstance(head, list) else [head]) + (tail if isinstance(tail, list) else [tail])
		for headOrTail in headsAndTails:
			if abs(float(headOrTail.x) - xLowerBoundary) < SPAresabs: internalPortOnXLowerBoundary = True
			if abs(float(headOrTail.x) - xUpperBoundary) < SPAresabs: internalPortOnXUpperBoundary = True
			if abs(float(headOrTail.y) - yLowerBoundary) < SPAresabs: internalPortOnYLowerBoundary = True
			if abs(float(headOrTail.y) - yUpperBoundary) < SPAresabs: internalPortOnYUpperBoundary = True
			if abs(float(headOrTail.z) - zLowerBoundary) < SPAresabs: internalPortOnZLowerBoundary = True
			if abs(float(headOrTail.z) - zUpperBoundary) < SPAresabs: internalPortOnZUpperBoundary = True
		head=V("(0.054305) - (0)","(0.0497925) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
		tail=V("(0.054305) - (0)","(0.0497925) - (0)","(((mask_top_layer_Zmax) + (mask_top_layer_Zmin)) / (2)) - (0)")
		extent=empro.components.CylindricalExtent("0.000146025","0.000146025")
		port = self._create_internal_port("P2","50 ohm Voltage Source",head,tail,extent)
		portShortcutGroups.append((6,port))
		ports.append(port)
		self._set_extra_port_info(port, "inputOutput", 2, "P2", "Direct")
		headsAndTails = (head if isinstance(head, list) else [head]) + (tail if isinstance(tail, list) else [tail])
		for headOrTail in headsAndTails:
			if abs(float(headOrTail.x) - xLowerBoundary) < SPAresabs: internalPortOnXLowerBoundary = True
			if abs(float(headOrTail.x) - xUpperBoundary) < SPAresabs: internalPortOnXUpperBoundary = True
			if abs(float(headOrTail.y) - yLowerBoundary) < SPAresabs: internalPortOnYLowerBoundary = True
			if abs(float(headOrTail.y) - yUpperBoundary) < SPAresabs: internalPortOnYUpperBoundary = True
			if abs(float(headOrTail.z) - zLowerBoundary) < SPAresabs: internalPortOnZLowerBoundary = True
			if abs(float(headOrTail.z) - zUpperBoundary) < SPAresabs: internalPortOnZUpperBoundary = True
		head=V("(0.060295) - (0)","(0.0548725) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
		tail=V("(0.060295) - (0)","(0.0548725) - (0)","(((mask_top_layer_Zmax) + (mask_top_layer_Zmin)) / (2)) - (0)")
		extent=empro.components.CylindricalExtent("0.000155925","0.000155925")
		port = self._create_internal_port("P3","50 ohm Voltage Source",head,tail,extent)
		portShortcutGroups.append((1,port))
		ports.append(port)
		self._set_extra_port_info(port, "inputOutput", 3, "P3", "Direct")
		headsAndTails = (head if isinstance(head, list) else [head]) + (tail if isinstance(tail, list) else [tail])
		for headOrTail in headsAndTails:
			if abs(float(headOrTail.x) - xLowerBoundary) < SPAresabs: internalPortOnXLowerBoundary = True
			if abs(float(headOrTail.x) - xUpperBoundary) < SPAresabs: internalPortOnXUpperBoundary = True
			if abs(float(headOrTail.y) - yLowerBoundary) < SPAresabs: internalPortOnYLowerBoundary = True
			if abs(float(headOrTail.y) - yUpperBoundary) < SPAresabs: internalPortOnYUpperBoundary = True
			if abs(float(headOrTail.z) - zLowerBoundary) < SPAresabs: internalPortOnZLowerBoundary = True
			if abs(float(headOrTail.z) - zUpperBoundary) < SPAresabs: internalPortOnZUpperBoundary = True
		head=V("(0.0603225) - (0)","(0.049755) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
		tail=V("(0.0603225) - (0)","(0.049755) - (0)","(((mask_top_layer_Zmax) + (mask_top_layer_Zmin)) / (2)) - (0)")
		extent=empro.components.CylindricalExtent("0.00016335","0.00016335")
		port = self._create_internal_port("P4","50 ohm Voltage Source",head,tail,extent)
		portShortcutGroups.append((4,port))
		ports.append(port)
		self._set_extra_port_info(port, "inputOutput", 4, "P4", "Direct")
		headsAndTails = (head if isinstance(head, list) else [head]) + (tail if isinstance(tail, list) else [tail])
		for headOrTail in headsAndTails:
			if abs(float(headOrTail.x) - xLowerBoundary) < SPAresabs: internalPortOnXLowerBoundary = True
			if abs(float(headOrTail.x) - xUpperBoundary) < SPAresabs: internalPortOnXUpperBoundary = True
			if abs(float(headOrTail.y) - yLowerBoundary) < SPAresabs: internalPortOnYLowerBoundary = True
			if abs(float(headOrTail.y) - yUpperBoundary) < SPAresabs: internalPortOnYUpperBoundary = True
			if abs(float(headOrTail.z) - zLowerBoundary) < SPAresabs: internalPortOnZLowerBoundary = True
			if abs(float(headOrTail.z) - zUpperBoundary) < SPAresabs: internalPortOnZUpperBoundary = True
		head=V("(0.061525) - (0)","(0.02687) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
		tail=V("(0.061525) - (0)","(0.02687) - (0)","(((mask_top_layer_Zmax) + (mask_top_layer_Zmin)) / (2)) - (0)")
		extent=empro.components.CylindricalExtent("0.00015345","0.00015345")
		port = self._create_internal_port("P5","50 ohm Voltage Source",head,tail,extent)
		portShortcutGroups.append((4,port))
		ports.append(port)
		self._set_extra_port_info(port, "inputOutput", 5, "P5", "Direct")
		headsAndTails = (head if isinstance(head, list) else [head]) + (tail if isinstance(tail, list) else [tail])
		for headOrTail in headsAndTails:
			if abs(float(headOrTail.x) - xLowerBoundary) < SPAresabs: internalPortOnXLowerBoundary = True
			if abs(float(headOrTail.x) - xUpperBoundary) < SPAresabs: internalPortOnXUpperBoundary = True
			if abs(float(headOrTail.y) - yLowerBoundary) < SPAresabs: internalPortOnYLowerBoundary = True
			if abs(float(headOrTail.y) - yUpperBoundary) < SPAresabs: internalPortOnYUpperBoundary = True
			if abs(float(headOrTail.z) - zLowerBoundary) < SPAresabs: internalPortOnZLowerBoundary = True
			if abs(float(headOrTail.z) - zUpperBoundary) < SPAresabs: internalPortOnZUpperBoundary = True
		head=V("(0.0675325) - (0)","(0.03191) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
		tail=V("(0.0675325) - (0)","(0.03191) - (0)","(((mask_top_layer_Zmax) + (mask_top_layer_Zmin)) / (2)) - (0)")
		extent=empro.components.CylindricalExtent("0.00018315","0.00018315")
		port = self._create_internal_port("P6","50 ohm Voltage Source",head,tail,extent)
		portShortcutGroups.append((2,port))
		ports.append(port)
		self._set_extra_port_info(port, "inputOutput", 6, "P6", "Direct")
		headsAndTails = (head if isinstance(head, list) else [head]) + (tail if isinstance(tail, list) else [tail])
		for headOrTail in headsAndTails:
			if abs(float(headOrTail.x) - xLowerBoundary) < SPAresabs: internalPortOnXLowerBoundary = True
			if abs(float(headOrTail.x) - xUpperBoundary) < SPAresabs: internalPortOnXUpperBoundary = True
			if abs(float(headOrTail.y) - yLowerBoundary) < SPAresabs: internalPortOnYLowerBoundary = True
			if abs(float(headOrTail.y) - yUpperBoundary) < SPAresabs: internalPortOnYUpperBoundary = True
			if abs(float(headOrTail.z) - zLowerBoundary) < SPAresabs: internalPortOnZLowerBoundary = True
			if abs(float(headOrTail.z) - zUpperBoundary) < SPAresabs: internalPortOnZUpperBoundary = True
		head=V("(0.0674775) - (0)","(0.026785) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
		tail=V("(0.0674775) - (0)","(0.026785) - (0)","(((mask_top_layer_Zmax) + (mask_top_layer_Zmin)) / (2)) - (0)")
		extent=empro.components.CylindricalExtent("0.0002376","0.0002376")
		port = self._create_internal_port("P7","50 ohm Voltage Source",head,tail,extent)
		portShortcutGroups.append((7,port))
		ports.append(port)
		self._set_extra_port_info(port, "inputOutput", 7, "P7", "Direct")
		headsAndTails = (head if isinstance(head, list) else [head]) + (tail if isinstance(tail, list) else [tail])
		for headOrTail in headsAndTails:
			if abs(float(headOrTail.x) - xLowerBoundary) < SPAresabs: internalPortOnXLowerBoundary = True
			if abs(float(headOrTail.x) - xUpperBoundary) < SPAresabs: internalPortOnXUpperBoundary = True
			if abs(float(headOrTail.y) - yLowerBoundary) < SPAresabs: internalPortOnYLowerBoundary = True
			if abs(float(headOrTail.y) - yUpperBoundary) < SPAresabs: internalPortOnYUpperBoundary = True
			if abs(float(headOrTail.z) - zLowerBoundary) < SPAresabs: internalPortOnZLowerBoundary = True
			if abs(float(headOrTail.z) - zUpperBoundary) < SPAresabs: internalPortOnZUpperBoundary = True
		head=V("(0.03139) - (0)","(0.070685) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
		tail=V("(0.03139) - (0)","(0.070685) - (0)","(((mask_top_layer_Zmax) + (mask_top_layer_Zmin)) / (2)) - (0)")
		extent=empro.components.CylindricalExtent("0.00020295","0.00020295")
		port = self._create_internal_port("P8","50 ohm Voltage Source",head,tail,extent)
		portShortcutGroups.append((5,port))
		ports.append(port)
		self._set_extra_port_info(port, "inputOutput", 8, "P8", "Direct")
		headsAndTails = (head if isinstance(head, list) else [head]) + (tail if isinstance(tail, list) else [tail])
		for headOrTail in headsAndTails:
			if abs(float(headOrTail.x) - xLowerBoundary) < SPAresabs: internalPortOnXLowerBoundary = True
			if abs(float(headOrTail.x) - xUpperBoundary) < SPAresabs: internalPortOnXUpperBoundary = True
			if abs(float(headOrTail.y) - yLowerBoundary) < SPAresabs: internalPortOnYLowerBoundary = True
			if abs(float(headOrTail.y) - yUpperBoundary) < SPAresabs: internalPortOnYUpperBoundary = True
			if abs(float(headOrTail.z) - zLowerBoundary) < SPAresabs: internalPortOnZLowerBoundary = True
			if abs(float(headOrTail.z) - zUpperBoundary) < SPAresabs: internalPortOnZUpperBoundary = True
		head=V("(0.037325) - (0)","(0.075745) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
		tail=V("(0.037325) - (0)","(0.075745) - (0)","(((mask_top_layer_Zmax) + (mask_top_layer_Zmin)) / (2)) - (0)")
		extent=empro.components.CylindricalExtent("0.00017325","0.00017325")
		port = self._create_internal_port("P9","50 ohm Voltage Source",head,tail,extent)
		portShortcutGroups.append((1,port))
		ports.append(port)
		self._set_extra_port_info(port, "inputOutput", 9, "P9", "Direct")
		headsAndTails = (head if isinstance(head, list) else [head]) + (tail if isinstance(tail, list) else [tail])
		for headOrTail in headsAndTails:
			if abs(float(headOrTail.x) - xLowerBoundary) < SPAresabs: internalPortOnXLowerBoundary = True
			if abs(float(headOrTail.x) - xUpperBoundary) < SPAresabs: internalPortOnXUpperBoundary = True
			if abs(float(headOrTail.y) - yLowerBoundary) < SPAresabs: internalPortOnYLowerBoundary = True
			if abs(float(headOrTail.y) - yUpperBoundary) < SPAresabs: internalPortOnYUpperBoundary = True
			if abs(float(headOrTail.z) - zLowerBoundary) < SPAresabs: internalPortOnZLowerBoundary = True
			if abs(float(headOrTail.z) - zUpperBoundary) < SPAresabs: internalPortOnZUpperBoundary = True
		head=V("(0.031465) - (0)","(0.0757625) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
		tail=V("(0.031465) - (0)","(0.0757625) - (0)","(((mask_top_layer_Zmax) + (mask_top_layer_Zmin)) / (2)) - (0)")
		extent=empro.components.CylindricalExtent("0.000190575","0.000190575")
		port = self._create_internal_port("P10","50 ohm Voltage Source",head,tail,extent)
		portShortcutGroups.append((3,port))
		ports.append(port)
		self._set_extra_port_info(port, "inputOutput", 10, "P10", "Direct")
		headsAndTails = (head if isinstance(head, list) else [head]) + (tail if isinstance(tail, list) else [tail])
		for headOrTail in headsAndTails:
			if abs(float(headOrTail.x) - xLowerBoundary) < SPAresabs: internalPortOnXLowerBoundary = True
			if abs(float(headOrTail.x) - xUpperBoundary) < SPAresabs: internalPortOnXUpperBoundary = True
			if abs(float(headOrTail.y) - yLowerBoundary) < SPAresabs: internalPortOnYLowerBoundary = True
			if abs(float(headOrTail.y) - yUpperBoundary) < SPAresabs: internalPortOnYUpperBoundary = True
			if abs(float(headOrTail.z) - zLowerBoundary) < SPAresabs: internalPortOnZLowerBoundary = True
			if abs(float(headOrTail.z) - zUpperBoundary) < SPAresabs: internalPortOnZUpperBoundary = True
		if includeInvalidPorts:
			head=V("(0.049999989) - (0)","(0.049860368) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			tail=V("(0.049999989) - (0)","(0.049860368) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			extent=None
			port = self._create_internal_port("J1_1","50 ohm Voltage Source",head,tail,extent)
			portShortcutGroups.append((6,port))
			ports.append(port)
			self._set_extra_port_info(port, "inputOutput", 11, "J1_1", "Direct")
			headsAndTails = (head if isinstance(head, list) else [head]) + (tail if isinstance(tail, list) else [tail])
			for headOrTail in headsAndTails:
				if abs(float(headOrTail.x) - xLowerBoundary) < SPAresabs: internalPortOnXLowerBoundary = True
				if abs(float(headOrTail.x) - xUpperBoundary) < SPAresabs: internalPortOnXUpperBoundary = True
				if abs(float(headOrTail.y) - yLowerBoundary) < SPAresabs: internalPortOnYLowerBoundary = True
				if abs(float(headOrTail.y) - yUpperBoundary) < SPAresabs: internalPortOnYUpperBoundary = True
				if abs(float(headOrTail.z) - zLowerBoundary) < SPAresabs: internalPortOnZLowerBoundary = True
				if abs(float(headOrTail.z) - zUpperBoundary) < SPAresabs: internalPortOnZUpperBoundary = True
		if includeInvalidPorts:
			head=V("(0.051269989) - (0)","(0.051130368) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			tail=V("(0.051269989) - (0)","(0.051130368) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			extent=None
			port = self._create_internal_port("J1_2","50 ohm Voltage Source",head,tail,extent)
			portShortcutGroups.append((0,port))
			ports.append(port)
			self._set_extra_port_info(port, "inputOutput", 12, "J1_2", "Direct")
			headsAndTails = (head if isinstance(head, list) else [head]) + (tail if isinstance(tail, list) else [tail])
			for headOrTail in headsAndTails:
				if abs(float(headOrTail.x) - xLowerBoundary) < SPAresabs: internalPortOnXLowerBoundary = True
				if abs(float(headOrTail.x) - xUpperBoundary) < SPAresabs: internalPortOnXUpperBoundary = True
				if abs(float(headOrTail.y) - yLowerBoundary) < SPAresabs: internalPortOnYLowerBoundary = True
				if abs(float(headOrTail.y) - yUpperBoundary) < SPAresabs: internalPortOnYUpperBoundary = True
				if abs(float(headOrTail.z) - zLowerBoundary) < SPAresabs: internalPortOnZLowerBoundary = True
				if abs(float(headOrTail.z) - zUpperBoundary) < SPAresabs: internalPortOnZUpperBoundary = True
		if includeInvalidPorts:
			head=V("(0.051269989) - (0)","(0.048590368) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			tail=V("(0.051269989) - (0)","(0.048590368) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			extent=None
			port = self._create_internal_port("J1_3","50 ohm Voltage Source",head,tail,extent)
			portShortcutGroups.append((0,port))
			ports.append(port)
			self._set_extra_port_info(port, "inputOutput", 13, "J1_3", "Direct")
			headsAndTails = (head if isinstance(head, list) else [head]) + (tail if isinstance(tail, list) else [tail])
			for headOrTail in headsAndTails:
				if abs(float(headOrTail.x) - xLowerBoundary) < SPAresabs: internalPortOnXLowerBoundary = True
				if abs(float(headOrTail.x) - xUpperBoundary) < SPAresabs: internalPortOnXUpperBoundary = True
				if abs(float(headOrTail.y) - yLowerBoundary) < SPAresabs: internalPortOnYLowerBoundary = True
				if abs(float(headOrTail.y) - yUpperBoundary) < SPAresabs: internalPortOnYUpperBoundary = True
				if abs(float(headOrTail.z) - zLowerBoundary) < SPAresabs: internalPortOnZLowerBoundary = True
				if abs(float(headOrTail.z) - zUpperBoundary) < SPAresabs: internalPortOnZUpperBoundary = True
		if includeInvalidPorts:
			head=V("(0.048729989) - (0)","(0.048590368) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			tail=V("(0.048729989) - (0)","(0.048590368) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			extent=None
			port = self._create_internal_port("J1_4","50 ohm Voltage Source",head,tail,extent)
			portShortcutGroups.append((0,port))
			ports.append(port)
			self._set_extra_port_info(port, "inputOutput", 14, "J1_4", "Direct")
			headsAndTails = (head if isinstance(head, list) else [head]) + (tail if isinstance(tail, list) else [tail])
			for headOrTail in headsAndTails:
				if abs(float(headOrTail.x) - xLowerBoundary) < SPAresabs: internalPortOnXLowerBoundary = True
				if abs(float(headOrTail.x) - xUpperBoundary) < SPAresabs: internalPortOnXUpperBoundary = True
				if abs(float(headOrTail.y) - yLowerBoundary) < SPAresabs: internalPortOnYLowerBoundary = True
				if abs(float(headOrTail.y) - yUpperBoundary) < SPAresabs: internalPortOnYUpperBoundary = True
				if abs(float(headOrTail.z) - zLowerBoundary) < SPAresabs: internalPortOnZLowerBoundary = True
				if abs(float(headOrTail.z) - zUpperBoundary) < SPAresabs: internalPortOnZUpperBoundary = True
		if includeInvalidPorts:
			head=V("(0.048729989) - (0)","(0.051130368) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			tail=V("(0.048729989) - (0)","(0.051130368) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			extent=None
			port = self._create_internal_port("J1_5","50 ohm Voltage Source",head,tail,extent)
			portShortcutGroups.append((0,port))
			ports.append(port)
			self._set_extra_port_info(port, "inputOutput", 15, "J1_5", "Direct")
			headsAndTails = (head if isinstance(head, list) else [head]) + (tail if isinstance(tail, list) else [tail])
			for headOrTail in headsAndTails:
				if abs(float(headOrTail.x) - xLowerBoundary) < SPAresabs: internalPortOnXLowerBoundary = True
				if abs(float(headOrTail.x) - xUpperBoundary) < SPAresabs: internalPortOnXUpperBoundary = True
				if abs(float(headOrTail.y) - yLowerBoundary) < SPAresabs: internalPortOnYLowerBoundary = True
				if abs(float(headOrTail.y) - yUpperBoundary) < SPAresabs: internalPortOnYUpperBoundary = True
				if abs(float(headOrTail.z) - zLowerBoundary) < SPAresabs: internalPortOnZLowerBoundary = True
				if abs(float(headOrTail.z) - zUpperBoundary) < SPAresabs: internalPortOnZUpperBoundary = True
		if includeInvalidPorts:
			head=V("(0.006801) - (0)","(0.049859999) - (0)","(((mask_top_layer_Zmax) + (mask_top_layer_Zmin)) / (2)) - (0)")
			tail=V("(0.006801) - (0)","(0.049859999) - (0)","(((mask_top_layer_Zmax) + (mask_top_layer_Zmin)) / (2)) - (0)")
			extent=None
			port = self._create_internal_port("P1_1","50 ohm Voltage Source",head,tail,extent)
			portShortcutGroups.append((5,port))
			ports.append(port)
			self._set_extra_port_info(port, "inputOutput", 16, "P1_1", "Direct")
			headsAndTails = (head if isinstance(head, list) else [head]) + (tail if isinstance(tail, list) else [tail])
			for headOrTail in headsAndTails:
				if abs(float(headOrTail.x) - xLowerBoundary) < SPAresabs: internalPortOnXLowerBoundary = True
				if abs(float(headOrTail.x) - xUpperBoundary) < SPAresabs: internalPortOnXUpperBoundary = True
				if abs(float(headOrTail.y) - yLowerBoundary) < SPAresabs: internalPortOnYLowerBoundary = True
				if abs(float(headOrTail.y) - yUpperBoundary) < SPAresabs: internalPortOnYUpperBoundary = True
				if abs(float(headOrTail.z) - zLowerBoundary) < SPAresabs: internalPortOnZLowerBoundary = True
				if abs(float(headOrTail.z) - zUpperBoundary) < SPAresabs: internalPortOnZUpperBoundary = True
		if includeInvalidPorts:
			head=V("(0.050038) - (0)","(0.093109999) - (0)","(((mask_top_layer_Zmax) + (mask_top_layer_Zmin)) / (2)) - (0)")
			tail=V("(0.050038) - (0)","(0.093109999) - (0)","(((mask_top_layer_Zmax) + (mask_top_layer_Zmin)) / (2)) - (0)")
			extent=None
			port = self._create_internal_port("P2_1","50 ohm Voltage Source",head,tail,extent)
			portShortcutGroups.append((3,port))
			ports.append(port)
			self._set_extra_port_info(port, "inputOutput", 17, "P2_1", "Direct")
			headsAndTails = (head if isinstance(head, list) else [head]) + (tail if isinstance(tail, list) else [tail])
			for headOrTail in headsAndTails:
				if abs(float(headOrTail.x) - xLowerBoundary) < SPAresabs: internalPortOnXLowerBoundary = True
				if abs(float(headOrTail.x) - xUpperBoundary) < SPAresabs: internalPortOnXUpperBoundary = True
				if abs(float(headOrTail.y) - yLowerBoundary) < SPAresabs: internalPortOnYLowerBoundary = True
				if abs(float(headOrTail.y) - yUpperBoundary) < SPAresabs: internalPortOnYUpperBoundary = True
				if abs(float(headOrTail.z) - zLowerBoundary) < SPAresabs: internalPortOnZLowerBoundary = True
				if abs(float(headOrTail.z) - zUpperBoundary) < SPAresabs: internalPortOnZUpperBoundary = True
		if includeInvalidPorts:
			head=V("(0.093301002) - (0)","(0.049859999) - (0)","(((mask_top_layer_Zmax) + (mask_top_layer_Zmin)) / (2)) - (0)")
			tail=V("(0.093301002) - (0)","(0.049859999) - (0)","(((mask_top_layer_Zmax) + (mask_top_layer_Zmin)) / (2)) - (0)")
			extent=None
			port = self._create_internal_port("P3_1","50 ohm Voltage Source",head,tail,extent)
			portShortcutGroups.append((2,port))
			ports.append(port)
			self._set_extra_port_info(port, "inputOutput", 18, "P3_1", "Direct")
			headsAndTails = (head if isinstance(head, list) else [head]) + (tail if isinstance(tail, list) else [tail])
			for headOrTail in headsAndTails:
				if abs(float(headOrTail.x) - xLowerBoundary) < SPAresabs: internalPortOnXLowerBoundary = True
				if abs(float(headOrTail.x) - xUpperBoundary) < SPAresabs: internalPortOnXUpperBoundary = True
				if abs(float(headOrTail.y) - yLowerBoundary) < SPAresabs: internalPortOnYLowerBoundary = True
				if abs(float(headOrTail.y) - yUpperBoundary) < SPAresabs: internalPortOnYUpperBoundary = True
				if abs(float(headOrTail.z) - zLowerBoundary) < SPAresabs: internalPortOnZLowerBoundary = True
				if abs(float(headOrTail.z) - zUpperBoundary) < SPAresabs: internalPortOnZUpperBoundary = True
		if includeInvalidPorts:
			head=V("(0.050038003) - (0)","(0.006609999) - (0)","(((mask_top_layer_Zmax) + (mask_top_layer_Zmin)) / (2)) - (0)")
			tail=V("(0.050038003) - (0)","(0.006609999) - (0)","(((mask_top_layer_Zmax) + (mask_top_layer_Zmin)) / (2)) - (0)")
			extent=None
			port = self._create_internal_port("P4_1","50 ohm Voltage Source",head,tail,extent)
			portShortcutGroups.append((7,port))
			ports.append(port)
			self._set_extra_port_info(port, "inputOutput", 19, "P4_1", "Direct")
			headsAndTails = (head if isinstance(head, list) else [head]) + (tail if isinstance(tail, list) else [tail])
			for headOrTail in headsAndTails:
				if abs(float(headOrTail.x) - xLowerBoundary) < SPAresabs: internalPortOnXLowerBoundary = True
				if abs(float(headOrTail.x) - xUpperBoundary) < SPAresabs: internalPortOnXUpperBoundary = True
				if abs(float(headOrTail.y) - yLowerBoundary) < SPAresabs: internalPortOnYLowerBoundary = True
				if abs(float(headOrTail.y) - yUpperBoundary) < SPAresabs: internalPortOnYUpperBoundary = True
				if abs(float(headOrTail.z) - zLowerBoundary) < SPAresabs: internalPortOnZLowerBoundary = True
				if abs(float(headOrTail.z) - zUpperBoundary) < SPAresabs: internalPortOnZUpperBoundary = True
		if includeInvalidPorts:
			head=V("(0.037338) - (0)","(0.075692) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			tail=V("(0.037338) - (0)","(0.075692) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			extent=None
			port = self._create_internal_port("U1_1","50 ohm Voltage Source",head,tail,extent)
			portShortcutGroups.append((1,port))
			ports.append(port)
			self._set_extra_port_info(port, "inputOutput", 20, "U1_1", "Direct")
			headsAndTails = (head if isinstance(head, list) else [head]) + (tail if isinstance(tail, list) else [tail])
			for headOrTail in headsAndTails:
				if abs(float(headOrTail.x) - xLowerBoundary) < SPAresabs: internalPortOnXLowerBoundary = True
				if abs(float(headOrTail.x) - xUpperBoundary) < SPAresabs: internalPortOnXUpperBoundary = True
				if abs(float(headOrTail.y) - yLowerBoundary) < SPAresabs: internalPortOnYLowerBoundary = True
				if abs(float(headOrTail.y) - yUpperBoundary) < SPAresabs: internalPortOnYUpperBoundary = True
				if abs(float(headOrTail.z) - zLowerBoundary) < SPAresabs: internalPortOnZLowerBoundary = True
				if abs(float(headOrTail.z) - zUpperBoundary) < SPAresabs: internalPortOnZUpperBoundary = True
		if includeInvalidPorts:
			head=V("(0.037338) - (0)","(0.074422) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			tail=V("(0.037338) - (0)","(0.074422) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			extent=None
			port = self._create_internal_port("U1_2","50 ohm Voltage Source",head,tail,extent)
			portShortcutGroups.append((0,port))
			ports.append(port)
			self._set_extra_port_info(port, "inputOutput", 21, "U1_2", "Direct")
			headsAndTails = (head if isinstance(head, list) else [head]) + (tail if isinstance(tail, list) else [tail])
			for headOrTail in headsAndTails:
				if abs(float(headOrTail.x) - xLowerBoundary) < SPAresabs: internalPortOnXLowerBoundary = True
				if abs(float(headOrTail.x) - xUpperBoundary) < SPAresabs: internalPortOnXUpperBoundary = True
				if abs(float(headOrTail.y) - yLowerBoundary) < SPAresabs: internalPortOnYLowerBoundary = True
				if abs(float(headOrTail.y) - yUpperBoundary) < SPAresabs: internalPortOnYUpperBoundary = True
				if abs(float(headOrTail.z) - zLowerBoundary) < SPAresabs: internalPortOnZLowerBoundary = True
				if abs(float(headOrTail.z) - zUpperBoundary) < SPAresabs: internalPortOnZUpperBoundary = True
		if includeInvalidPorts:
			head=V("(0.037338) - (0)","(0.073152) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			tail=V("(0.037338) - (0)","(0.073152) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			extent=None
			port = self._create_internal_port("U1_3","50 ohm Voltage Source",head,tail,extent)
			portShortcutGroups.append((0,port))
			ports.append(port)
			self._set_extra_port_info(port, "inputOutput", 22, "U1_3", "Direct")
			headsAndTails = (head if isinstance(head, list) else [head]) + (tail if isinstance(tail, list) else [tail])
			for headOrTail in headsAndTails:
				if abs(float(headOrTail.x) - xLowerBoundary) < SPAresabs: internalPortOnXLowerBoundary = True
				if abs(float(headOrTail.x) - xUpperBoundary) < SPAresabs: internalPortOnXUpperBoundary = True
				if abs(float(headOrTail.y) - yLowerBoundary) < SPAresabs: internalPortOnYLowerBoundary = True
				if abs(float(headOrTail.y) - yUpperBoundary) < SPAresabs: internalPortOnYUpperBoundary = True
				if abs(float(headOrTail.z) - zLowerBoundary) < SPAresabs: internalPortOnZLowerBoundary = True
				if abs(float(headOrTail.z) - zUpperBoundary) < SPAresabs: internalPortOnZUpperBoundary = True
		if includeInvalidPorts:
			head=V("(0.037338) - (0)","(0.071882) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			tail=V("(0.037338) - (0)","(0.071882) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			extent=None
			port = self._create_internal_port("U1_4","50 ohm Voltage Source",head,tail,extent)
			portShortcutGroups.append((0,port))
			ports.append(port)
			self._set_extra_port_info(port, "inputOutput", 23, "U1_4", "Direct")
			headsAndTails = (head if isinstance(head, list) else [head]) + (tail if isinstance(tail, list) else [tail])
			for headOrTail in headsAndTails:
				if abs(float(headOrTail.x) - xLowerBoundary) < SPAresabs: internalPortOnXLowerBoundary = True
				if abs(float(headOrTail.x) - xUpperBoundary) < SPAresabs: internalPortOnXUpperBoundary = True
				if abs(float(headOrTail.y) - yLowerBoundary) < SPAresabs: internalPortOnYLowerBoundary = True
				if abs(float(headOrTail.y) - yUpperBoundary) < SPAresabs: internalPortOnYUpperBoundary = True
				if abs(float(headOrTail.z) - zLowerBoundary) < SPAresabs: internalPortOnZLowerBoundary = True
				if abs(float(headOrTail.z) - zUpperBoundary) < SPAresabs: internalPortOnZUpperBoundary = True
		if includeInvalidPorts:
			head=V("(0.037338) - (0)","(0.070612) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			tail=V("(0.037338) - (0)","(0.070612) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			extent=None
			port = self._create_internal_port("U1_5","50 ohm Voltage Source",head,tail,extent)
			portShortcutGroups.append((9,port))
			ports.append(port)
			self._set_extra_port_info(port, "inputOutput", 24, "U1_5", "Direct")
			headsAndTails = (head if isinstance(head, list) else [head]) + (tail if isinstance(tail, list) else [tail])
			for headOrTail in headsAndTails:
				if abs(float(headOrTail.x) - xLowerBoundary) < SPAresabs: internalPortOnXLowerBoundary = True
				if abs(float(headOrTail.x) - xUpperBoundary) < SPAresabs: internalPortOnXUpperBoundary = True
				if abs(float(headOrTail.y) - yLowerBoundary) < SPAresabs: internalPortOnYLowerBoundary = True
				if abs(float(headOrTail.y) - yUpperBoundary) < SPAresabs: internalPortOnYUpperBoundary = True
				if abs(float(headOrTail.z) - zLowerBoundary) < SPAresabs: internalPortOnZLowerBoundary = True
				if abs(float(headOrTail.z) - zUpperBoundary) < SPAresabs: internalPortOnZUpperBoundary = True
		if includeInvalidPorts:
			head=V("(0.031407001) - (0)","(0.070612) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			tail=V("(0.031407001) - (0)","(0.070612) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			extent=None
			port = self._create_internal_port("U1_6","50 ohm Voltage Source",head,tail,extent)
			portShortcutGroups.append((5,port))
			ports.append(port)
			self._set_extra_port_info(port, "inputOutput", 25, "U1_6", "Direct")
			headsAndTails = (head if isinstance(head, list) else [head]) + (tail if isinstance(tail, list) else [tail])
			for headOrTail in headsAndTails:
				if abs(float(headOrTail.x) - xLowerBoundary) < SPAresabs: internalPortOnXLowerBoundary = True
				if abs(float(headOrTail.x) - xUpperBoundary) < SPAresabs: internalPortOnXUpperBoundary = True
				if abs(float(headOrTail.y) - yLowerBoundary) < SPAresabs: internalPortOnYLowerBoundary = True
				if abs(float(headOrTail.y) - yUpperBoundary) < SPAresabs: internalPortOnYUpperBoundary = True
				if abs(float(headOrTail.z) - zLowerBoundary) < SPAresabs: internalPortOnZLowerBoundary = True
				if abs(float(headOrTail.z) - zUpperBoundary) < SPAresabs: internalPortOnZUpperBoundary = True
		if includeInvalidPorts:
			head=V("(0.031369) - (0)","(0.071882) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			tail=V("(0.031369) - (0)","(0.071882) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			extent=None
			port = self._create_internal_port("U1_7","50 ohm Voltage Source",head,tail,extent)
			portShortcutGroups.append((0,port))
			ports.append(port)
			self._set_extra_port_info(port, "inputOutput", 26, "U1_7", "Direct")
			headsAndTails = (head if isinstance(head, list) else [head]) + (tail if isinstance(tail, list) else [tail])
			for headOrTail in headsAndTails:
				if abs(float(headOrTail.x) - xLowerBoundary) < SPAresabs: internalPortOnXLowerBoundary = True
				if abs(float(headOrTail.x) - xUpperBoundary) < SPAresabs: internalPortOnXUpperBoundary = True
				if abs(float(headOrTail.y) - yLowerBoundary) < SPAresabs: internalPortOnYLowerBoundary = True
				if abs(float(headOrTail.y) - yUpperBoundary) < SPAresabs: internalPortOnYUpperBoundary = True
				if abs(float(headOrTail.z) - zLowerBoundary) < SPAresabs: internalPortOnZLowerBoundary = True
				if abs(float(headOrTail.z) - zUpperBoundary) < SPAresabs: internalPortOnZUpperBoundary = True
		if includeInvalidPorts:
			head=V("(0.031369) - (0)","(0.073152) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			tail=V("(0.031369) - (0)","(0.073152) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			extent=None
			port = self._create_internal_port("U1_8","50 ohm Voltage Source",head,tail,extent)
			portShortcutGroups.append((0,port))
			ports.append(port)
			self._set_extra_port_info(port, "inputOutput", 27, "U1_8", "Direct")
			headsAndTails = (head if isinstance(head, list) else [head]) + (tail if isinstance(tail, list) else [tail])
			for headOrTail in headsAndTails:
				if abs(float(headOrTail.x) - xLowerBoundary) < SPAresabs: internalPortOnXLowerBoundary = True
				if abs(float(headOrTail.x) - xUpperBoundary) < SPAresabs: internalPortOnXUpperBoundary = True
				if abs(float(headOrTail.y) - yLowerBoundary) < SPAresabs: internalPortOnYLowerBoundary = True
				if abs(float(headOrTail.y) - yUpperBoundary) < SPAresabs: internalPortOnYUpperBoundary = True
				if abs(float(headOrTail.z) - zLowerBoundary) < SPAresabs: internalPortOnZLowerBoundary = True
				if abs(float(headOrTail.z) - zUpperBoundary) < SPAresabs: internalPortOnZUpperBoundary = True
		if includeInvalidPorts:
			head=V("(0.031369) - (0)","(0.074422) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			tail=V("(0.031369) - (0)","(0.074422) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			extent=None
			port = self._create_internal_port("U1_9","50 ohm Voltage Source",head,tail,extent)
			portShortcutGroups.append((0,port))
			ports.append(port)
			self._set_extra_port_info(port, "inputOutput", 28, "U1_9", "Direct")
			headsAndTails = (head if isinstance(head, list) else [head]) + (tail if isinstance(tail, list) else [tail])
			for headOrTail in headsAndTails:
				if abs(float(headOrTail.x) - xLowerBoundary) < SPAresabs: internalPortOnXLowerBoundary = True
				if abs(float(headOrTail.x) - xUpperBoundary) < SPAresabs: internalPortOnXUpperBoundary = True
				if abs(float(headOrTail.y) - yLowerBoundary) < SPAresabs: internalPortOnYLowerBoundary = True
				if abs(float(headOrTail.y) - yUpperBoundary) < SPAresabs: internalPortOnYUpperBoundary = True
				if abs(float(headOrTail.z) - zLowerBoundary) < SPAresabs: internalPortOnZLowerBoundary = True
				if abs(float(headOrTail.z) - zUpperBoundary) < SPAresabs: internalPortOnZUpperBoundary = True
		if includeInvalidPorts:
			head=V("(0.031407001) - (0)","(0.075692) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			tail=V("(0.031407001) - (0)","(0.075692) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			extent=None
			port = self._create_internal_port("U1_10","50 ohm Voltage Source",head,tail,extent)
			portShortcutGroups.append((3,port))
			ports.append(port)
			self._set_extra_port_info(port, "inputOutput", 29, "U1_10", "Direct")
			headsAndTails = (head if isinstance(head, list) else [head]) + (tail if isinstance(tail, list) else [tail])
			for headOrTail in headsAndTails:
				if abs(float(headOrTail.x) - xLowerBoundary) < SPAresabs: internalPortOnXLowerBoundary = True
				if abs(float(headOrTail.x) - xUpperBoundary) < SPAresabs: internalPortOnXUpperBoundary = True
				if abs(float(headOrTail.y) - yLowerBoundary) < SPAresabs: internalPortOnYLowerBoundary = True
				if abs(float(headOrTail.y) - yUpperBoundary) < SPAresabs: internalPortOnYUpperBoundary = True
				if abs(float(headOrTail.z) - zLowerBoundary) < SPAresabs: internalPortOnZLowerBoundary = True
				if abs(float(headOrTail.z) - zUpperBoundary) < SPAresabs: internalPortOnZUpperBoundary = True
		if includeInvalidPorts:
			head=V("(0.0343535) - (0)","(0.073152) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			tail=V("(0.0343535) - (0)","(0.073152) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			extent=None
			port = self._create_internal_port("U1_11","50 ohm Voltage Source",head,tail,extent)
			portShortcutGroups.append((0,port))
			ports.append(port)
			self._set_extra_port_info(port, "inputOutput", 30, "U1_11", "Direct")
			headsAndTails = (head if isinstance(head, list) else [head]) + (tail if isinstance(tail, list) else [tail])
			for headOrTail in headsAndTails:
				if abs(float(headOrTail.x) - xLowerBoundary) < SPAresabs: internalPortOnXLowerBoundary = True
				if abs(float(headOrTail.x) - xUpperBoundary) < SPAresabs: internalPortOnXUpperBoundary = True
				if abs(float(headOrTail.y) - yLowerBoundary) < SPAresabs: internalPortOnYLowerBoundary = True
				if abs(float(headOrTail.y) - yUpperBoundary) < SPAresabs: internalPortOnYUpperBoundary = True
				if abs(float(headOrTail.z) - zLowerBoundary) < SPAresabs: internalPortOnZLowerBoundary = True
				if abs(float(headOrTail.z) - zUpperBoundary) < SPAresabs: internalPortOnZUpperBoundary = True
		if includeInvalidPorts:
			head=V("(0.054320161) - (0)","(0.049777848) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			tail=V("(0.054320161) - (0)","(0.049777848) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			extent=None
			port = self._create_internal_port("U2_1","50 ohm Voltage Source",head,tail,extent)
			portShortcutGroups.append((6,port))
			ports.append(port)
			self._set_extra_port_info(port, "inputOutput", 31, "U2_1", "Direct")
			headsAndTails = (head if isinstance(head, list) else [head]) + (tail if isinstance(tail, list) else [tail])
			for headOrTail in headsAndTails:
				if abs(float(headOrTail.x) - xLowerBoundary) < SPAresabs: internalPortOnXLowerBoundary = True
				if abs(float(headOrTail.x) - xUpperBoundary) < SPAresabs: internalPortOnXUpperBoundary = True
				if abs(float(headOrTail.y) - yLowerBoundary) < SPAresabs: internalPortOnYLowerBoundary = True
				if abs(float(headOrTail.y) - yUpperBoundary) < SPAresabs: internalPortOnYUpperBoundary = True
				if abs(float(headOrTail.z) - zLowerBoundary) < SPAresabs: internalPortOnZLowerBoundary = True
				if abs(float(headOrTail.z) - zUpperBoundary) < SPAresabs: internalPortOnZUpperBoundary = True
		if includeInvalidPorts:
			head=V("(0.054320161) - (0)","(0.051047848) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			tail=V("(0.054320161) - (0)","(0.051047848) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			extent=None
			port = self._create_internal_port("U2_2","50 ohm Voltage Source",head,tail,extent)
			portShortcutGroups.append((0,port))
			ports.append(port)
			self._set_extra_port_info(port, "inputOutput", 32, "U2_2", "Direct")
			headsAndTails = (head if isinstance(head, list) else [head]) + (tail if isinstance(tail, list) else [tail])
			for headOrTail in headsAndTails:
				if abs(float(headOrTail.x) - xLowerBoundary) < SPAresabs: internalPortOnXLowerBoundary = True
				if abs(float(headOrTail.x) - xUpperBoundary) < SPAresabs: internalPortOnXUpperBoundary = True
				if abs(float(headOrTail.y) - yLowerBoundary) < SPAresabs: internalPortOnYLowerBoundary = True
				if abs(float(headOrTail.y) - yUpperBoundary) < SPAresabs: internalPortOnYUpperBoundary = True
				if abs(float(headOrTail.z) - zLowerBoundary) < SPAresabs: internalPortOnZLowerBoundary = True
				if abs(float(headOrTail.z) - zUpperBoundary) < SPAresabs: internalPortOnZUpperBoundary = True
		if includeInvalidPorts:
			head=V("(0.054320161) - (0)","(0.052317848) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			tail=V("(0.054320161) - (0)","(0.052317848) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			extent=None
			port = self._create_internal_port("U2_3","50 ohm Voltage Source",head,tail,extent)
			portShortcutGroups.append((0,port))
			ports.append(port)
			self._set_extra_port_info(port, "inputOutput", 33, "U2_3", "Direct")
			headsAndTails = (head if isinstance(head, list) else [head]) + (tail if isinstance(tail, list) else [tail])
			for headOrTail in headsAndTails:
				if abs(float(headOrTail.x) - xLowerBoundary) < SPAresabs: internalPortOnXLowerBoundary = True
				if abs(float(headOrTail.x) - xUpperBoundary) < SPAresabs: internalPortOnXUpperBoundary = True
				if abs(float(headOrTail.y) - yLowerBoundary) < SPAresabs: internalPortOnYLowerBoundary = True
				if abs(float(headOrTail.y) - yUpperBoundary) < SPAresabs: internalPortOnYUpperBoundary = True
				if abs(float(headOrTail.z) - zLowerBoundary) < SPAresabs: internalPortOnZLowerBoundary = True
				if abs(float(headOrTail.z) - zUpperBoundary) < SPAresabs: internalPortOnZUpperBoundary = True
		if includeInvalidPorts:
			head=V("(0.054320161) - (0)","(0.053587848) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			tail=V("(0.054320161) - (0)","(0.053587848) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			extent=None
			port = self._create_internal_port("U2_4","50 ohm Voltage Source",head,tail,extent)
			portShortcutGroups.append((0,port))
			ports.append(port)
			self._set_extra_port_info(port, "inputOutput", 34, "U2_4", "Direct")
			headsAndTails = (head if isinstance(head, list) else [head]) + (tail if isinstance(tail, list) else [tail])
			for headOrTail in headsAndTails:
				if abs(float(headOrTail.x) - xLowerBoundary) < SPAresabs: internalPortOnXLowerBoundary = True
				if abs(float(headOrTail.x) - xUpperBoundary) < SPAresabs: internalPortOnXUpperBoundary = True
				if abs(float(headOrTail.y) - yLowerBoundary) < SPAresabs: internalPortOnYLowerBoundary = True
				if abs(float(headOrTail.y) - yUpperBoundary) < SPAresabs: internalPortOnYUpperBoundary = True
				if abs(float(headOrTail.z) - zLowerBoundary) < SPAresabs: internalPortOnZLowerBoundary = True
				if abs(float(headOrTail.z) - zUpperBoundary) < SPAresabs: internalPortOnZUpperBoundary = True
		if includeInvalidPorts:
			head=V("(0.054320161) - (0)","(0.054857848) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			tail=V("(0.054320161) - (0)","(0.054857848) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			extent=None
			port = self._create_internal_port("U2_5","50 ohm Voltage Source",head,tail,extent)
			portShortcutGroups.append((8,port))
			ports.append(port)
			self._set_extra_port_info(port, "inputOutput", 35, "U2_5", "Direct")
			headsAndTails = (head if isinstance(head, list) else [head]) + (tail if isinstance(tail, list) else [tail])
			for headOrTail in headsAndTails:
				if abs(float(headOrTail.x) - xLowerBoundary) < SPAresabs: internalPortOnXLowerBoundary = True
				if abs(float(headOrTail.x) - xUpperBoundary) < SPAresabs: internalPortOnXUpperBoundary = True
				if abs(float(headOrTail.y) - yLowerBoundary) < SPAresabs: internalPortOnYLowerBoundary = True
				if abs(float(headOrTail.y) - yUpperBoundary) < SPAresabs: internalPortOnYUpperBoundary = True
				if abs(float(headOrTail.z) - zLowerBoundary) < SPAresabs: internalPortOnZLowerBoundary = True
				if abs(float(headOrTail.z) - zUpperBoundary) < SPAresabs: internalPortOnZUpperBoundary = True
		if includeInvalidPorts:
			head=V("(0.060289161) - (0)","(0.054857848) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			tail=V("(0.060289161) - (0)","(0.054857848) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			extent=None
			port = self._create_internal_port("U2_6","50 ohm Voltage Source",head,tail,extent)
			portShortcutGroups.append((1,port))
			ports.append(port)
			self._set_extra_port_info(port, "inputOutput", 36, "U2_6", "Direct")
			headsAndTails = (head if isinstance(head, list) else [head]) + (tail if isinstance(tail, list) else [tail])
			for headOrTail in headsAndTails:
				if abs(float(headOrTail.x) - xLowerBoundary) < SPAresabs: internalPortOnXLowerBoundary = True
				if abs(float(headOrTail.x) - xUpperBoundary) < SPAresabs: internalPortOnXUpperBoundary = True
				if abs(float(headOrTail.y) - yLowerBoundary) < SPAresabs: internalPortOnYLowerBoundary = True
				if abs(float(headOrTail.y) - yUpperBoundary) < SPAresabs: internalPortOnYUpperBoundary = True
				if abs(float(headOrTail.z) - zLowerBoundary) < SPAresabs: internalPortOnZLowerBoundary = True
				if abs(float(headOrTail.z) - zUpperBoundary) < SPAresabs: internalPortOnZUpperBoundary = True
		if includeInvalidPorts:
			head=V("(0.060289161) - (0)","(0.053587848) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			tail=V("(0.060289161) - (0)","(0.053587848) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			extent=None
			port = self._create_internal_port("U2_7","50 ohm Voltage Source",head,tail,extent)
			portShortcutGroups.append((0,port))
			ports.append(port)
			self._set_extra_port_info(port, "inputOutput", 37, "U2_7", "Direct")
			headsAndTails = (head if isinstance(head, list) else [head]) + (tail if isinstance(tail, list) else [tail])
			for headOrTail in headsAndTails:
				if abs(float(headOrTail.x) - xLowerBoundary) < SPAresabs: internalPortOnXLowerBoundary = True
				if abs(float(headOrTail.x) - xUpperBoundary) < SPAresabs: internalPortOnXUpperBoundary = True
				if abs(float(headOrTail.y) - yLowerBoundary) < SPAresabs: internalPortOnYLowerBoundary = True
				if abs(float(headOrTail.y) - yUpperBoundary) < SPAresabs: internalPortOnYUpperBoundary = True
				if abs(float(headOrTail.z) - zLowerBoundary) < SPAresabs: internalPortOnZLowerBoundary = True
				if abs(float(headOrTail.z) - zUpperBoundary) < SPAresabs: internalPortOnZUpperBoundary = True
		if includeInvalidPorts:
			head=V("(0.060289161) - (0)","(0.052317848) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			tail=V("(0.060289161) - (0)","(0.052317848) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			extent=None
			port = self._create_internal_port("U2_8","50 ohm Voltage Source",head,tail,extent)
			portShortcutGroups.append((0,port))
			ports.append(port)
			self._set_extra_port_info(port, "inputOutput", 38, "U2_8", "Direct")
			headsAndTails = (head if isinstance(head, list) else [head]) + (tail if isinstance(tail, list) else [tail])
			for headOrTail in headsAndTails:
				if abs(float(headOrTail.x) - xLowerBoundary) < SPAresabs: internalPortOnXLowerBoundary = True
				if abs(float(headOrTail.x) - xUpperBoundary) < SPAresabs: internalPortOnXUpperBoundary = True
				if abs(float(headOrTail.y) - yLowerBoundary) < SPAresabs: internalPortOnYLowerBoundary = True
				if abs(float(headOrTail.y) - yUpperBoundary) < SPAresabs: internalPortOnYUpperBoundary = True
				if abs(float(headOrTail.z) - zLowerBoundary) < SPAresabs: internalPortOnZLowerBoundary = True
				if abs(float(headOrTail.z) - zUpperBoundary) < SPAresabs: internalPortOnZUpperBoundary = True
		if includeInvalidPorts:
			head=V("(0.060289161) - (0)","(0.051047848) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			tail=V("(0.060289161) - (0)","(0.051047848) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			extent=None
			port = self._create_internal_port("U2_9","50 ohm Voltage Source",head,tail,extent)
			portShortcutGroups.append((0,port))
			ports.append(port)
			self._set_extra_port_info(port, "inputOutput", 39, "U2_9", "Direct")
			headsAndTails = (head if isinstance(head, list) else [head]) + (tail if isinstance(tail, list) else [tail])
			for headOrTail in headsAndTails:
				if abs(float(headOrTail.x) - xLowerBoundary) < SPAresabs: internalPortOnXLowerBoundary = True
				if abs(float(headOrTail.x) - xUpperBoundary) < SPAresabs: internalPortOnXUpperBoundary = True
				if abs(float(headOrTail.y) - yLowerBoundary) < SPAresabs: internalPortOnYLowerBoundary = True
				if abs(float(headOrTail.y) - yUpperBoundary) < SPAresabs: internalPortOnYUpperBoundary = True
				if abs(float(headOrTail.z) - zLowerBoundary) < SPAresabs: internalPortOnZLowerBoundary = True
				if abs(float(headOrTail.z) - zUpperBoundary) < SPAresabs: internalPortOnZUpperBoundary = True
		if includeInvalidPorts:
			head=V("(0.060289161) - (0)","(0.049777848) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			tail=V("(0.060289161) - (0)","(0.049777848) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			extent=None
			port = self._create_internal_port("U2_10","50 ohm Voltage Source",head,tail,extent)
			portShortcutGroups.append((4,port))
			ports.append(port)
			self._set_extra_port_info(port, "inputOutput", 40, "U2_10", "Direct")
			headsAndTails = (head if isinstance(head, list) else [head]) + (tail if isinstance(tail, list) else [tail])
			for headOrTail in headsAndTails:
				if abs(float(headOrTail.x) - xLowerBoundary) < SPAresabs: internalPortOnXLowerBoundary = True
				if abs(float(headOrTail.x) - xUpperBoundary) < SPAresabs: internalPortOnXUpperBoundary = True
				if abs(float(headOrTail.y) - yLowerBoundary) < SPAresabs: internalPortOnYLowerBoundary = True
				if abs(float(headOrTail.y) - yUpperBoundary) < SPAresabs: internalPortOnYUpperBoundary = True
				if abs(float(headOrTail.z) - zLowerBoundary) < SPAresabs: internalPortOnZLowerBoundary = True
				if abs(float(headOrTail.z) - zUpperBoundary) < SPAresabs: internalPortOnZUpperBoundary = True
		if includeInvalidPorts:
			head=V("(0.057304661) - (0)","(0.052317848) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			tail=V("(0.057304661) - (0)","(0.052317848) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			extent=None
			port = self._create_internal_port("U2_11","50 ohm Voltage Source",head,tail,extent)
			portShortcutGroups.append((0,port))
			ports.append(port)
			self._set_extra_port_info(port, "inputOutput", 41, "U2_11", "Direct")
			headsAndTails = (head if isinstance(head, list) else [head]) + (tail if isinstance(tail, list) else [tail])
			for headOrTail in headsAndTails:
				if abs(float(headOrTail.x) - xLowerBoundary) < SPAresabs: internalPortOnXLowerBoundary = True
				if abs(float(headOrTail.x) - xUpperBoundary) < SPAresabs: internalPortOnXUpperBoundary = True
				if abs(float(headOrTail.y) - yLowerBoundary) < SPAresabs: internalPortOnYLowerBoundary = True
				if abs(float(headOrTail.y) - yUpperBoundary) < SPAresabs: internalPortOnYUpperBoundary = True
				if abs(float(headOrTail.z) - zLowerBoundary) < SPAresabs: internalPortOnZLowerBoundary = True
				if abs(float(headOrTail.z) - zUpperBoundary) < SPAresabs: internalPortOnZUpperBoundary = True
		if includeInvalidPorts:
			head=V("(0.0615315) - (0)","(0.026797) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			tail=V("(0.0615315) - (0)","(0.026797) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			extent=None
			port = self._create_internal_port("U3_1","50 ohm Voltage Source",head,tail,extent)
			portShortcutGroups.append((4,port))
			ports.append(port)
			self._set_extra_port_info(port, "inputOutput", 42, "U3_1", "Direct")
			headsAndTails = (head if isinstance(head, list) else [head]) + (tail if isinstance(tail, list) else [tail])
			for headOrTail in headsAndTails:
				if abs(float(headOrTail.x) - xLowerBoundary) < SPAresabs: internalPortOnXLowerBoundary = True
				if abs(float(headOrTail.x) - xUpperBoundary) < SPAresabs: internalPortOnXUpperBoundary = True
				if abs(float(headOrTail.y) - yLowerBoundary) < SPAresabs: internalPortOnYLowerBoundary = True
				if abs(float(headOrTail.y) - yUpperBoundary) < SPAresabs: internalPortOnYUpperBoundary = True
				if abs(float(headOrTail.z) - zLowerBoundary) < SPAresabs: internalPortOnZLowerBoundary = True
				if abs(float(headOrTail.z) - zUpperBoundary) < SPAresabs: internalPortOnZUpperBoundary = True
		if includeInvalidPorts:
			head=V("(0.0615315) - (0)","(0.028067) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			tail=V("(0.0615315) - (0)","(0.028067) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			extent=None
			port = self._create_internal_port("U3_2","50 ohm Voltage Source",head,tail,extent)
			portShortcutGroups.append((0,port))
			ports.append(port)
			self._set_extra_port_info(port, "inputOutput", 43, "U3_2", "Direct")
			headsAndTails = (head if isinstance(head, list) else [head]) + (tail if isinstance(tail, list) else [tail])
			for headOrTail in headsAndTails:
				if abs(float(headOrTail.x) - xLowerBoundary) < SPAresabs: internalPortOnXLowerBoundary = True
				if abs(float(headOrTail.x) - xUpperBoundary) < SPAresabs: internalPortOnXUpperBoundary = True
				if abs(float(headOrTail.y) - yLowerBoundary) < SPAresabs: internalPortOnYLowerBoundary = True
				if abs(float(headOrTail.y) - yUpperBoundary) < SPAresabs: internalPortOnYUpperBoundary = True
				if abs(float(headOrTail.z) - zLowerBoundary) < SPAresabs: internalPortOnZLowerBoundary = True
				if abs(float(headOrTail.z) - zUpperBoundary) < SPAresabs: internalPortOnZUpperBoundary = True
		if includeInvalidPorts:
			head=V("(0.0615315) - (0)","(0.029337) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			tail=V("(0.0615315) - (0)","(0.029337) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			extent=None
			port = self._create_internal_port("U3_3","50 ohm Voltage Source",head,tail,extent)
			portShortcutGroups.append((0,port))
			ports.append(port)
			self._set_extra_port_info(port, "inputOutput", 44, "U3_3", "Direct")
			headsAndTails = (head if isinstance(head, list) else [head]) + (tail if isinstance(tail, list) else [tail])
			for headOrTail in headsAndTails:
				if abs(float(headOrTail.x) - xLowerBoundary) < SPAresabs: internalPortOnXLowerBoundary = True
				if abs(float(headOrTail.x) - xUpperBoundary) < SPAresabs: internalPortOnXUpperBoundary = True
				if abs(float(headOrTail.y) - yLowerBoundary) < SPAresabs: internalPortOnYLowerBoundary = True
				if abs(float(headOrTail.y) - yUpperBoundary) < SPAresabs: internalPortOnYUpperBoundary = True
				if abs(float(headOrTail.z) - zLowerBoundary) < SPAresabs: internalPortOnZLowerBoundary = True
				if abs(float(headOrTail.z) - zUpperBoundary) < SPAresabs: internalPortOnZUpperBoundary = True
		if includeInvalidPorts:
			head=V("(0.0615315) - (0)","(0.030607) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			tail=V("(0.0615315) - (0)","(0.030607) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			extent=None
			port = self._create_internal_port("U3_4","50 ohm Voltage Source",head,tail,extent)
			portShortcutGroups.append((0,port))
			ports.append(port)
			self._set_extra_port_info(port, "inputOutput", 45, "U3_4", "Direct")
			headsAndTails = (head if isinstance(head, list) else [head]) + (tail if isinstance(tail, list) else [tail])
			for headOrTail in headsAndTails:
				if abs(float(headOrTail.x) - xLowerBoundary) < SPAresabs: internalPortOnXLowerBoundary = True
				if abs(float(headOrTail.x) - xUpperBoundary) < SPAresabs: internalPortOnXUpperBoundary = True
				if abs(float(headOrTail.y) - yLowerBoundary) < SPAresabs: internalPortOnYLowerBoundary = True
				if abs(float(headOrTail.y) - yUpperBoundary) < SPAresabs: internalPortOnYUpperBoundary = True
				if abs(float(headOrTail.z) - zLowerBoundary) < SPAresabs: internalPortOnZLowerBoundary = True
				if abs(float(headOrTail.z) - zUpperBoundary) < SPAresabs: internalPortOnZUpperBoundary = True
		if includeInvalidPorts:
			head=V("(0.0615315) - (0)","(0.031877) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			tail=V("(0.0615315) - (0)","(0.031877) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			extent=None
			port = self._create_internal_port("U3_5","50 ohm Voltage Source",head,tail,extent)
			portShortcutGroups.append((10,port))
			ports.append(port)
			self._set_extra_port_info(port, "inputOutput", 46, "U3_5", "Direct")
			headsAndTails = (head if isinstance(head, list) else [head]) + (tail if isinstance(tail, list) else [tail])
			for headOrTail in headsAndTails:
				if abs(float(headOrTail.x) - xLowerBoundary) < SPAresabs: internalPortOnXLowerBoundary = True
				if abs(float(headOrTail.x) - xUpperBoundary) < SPAresabs: internalPortOnXUpperBoundary = True
				if abs(float(headOrTail.y) - yLowerBoundary) < SPAresabs: internalPortOnYLowerBoundary = True
				if abs(float(headOrTail.y) - yUpperBoundary) < SPAresabs: internalPortOnYUpperBoundary = True
				if abs(float(headOrTail.z) - zLowerBoundary) < SPAresabs: internalPortOnZLowerBoundary = True
				if abs(float(headOrTail.z) - zUpperBoundary) < SPAresabs: internalPortOnZUpperBoundary = True
		if includeInvalidPorts:
			head=V("(0.067538501) - (0)","(0.031877) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			tail=V("(0.067538501) - (0)","(0.031877) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			extent=None
			port = self._create_internal_port("U3_6","50 ohm Voltage Source",head,tail,extent)
			portShortcutGroups.append((2,port))
			ports.append(port)
			self._set_extra_port_info(port, "inputOutput", 47, "U3_6", "Direct")
			headsAndTails = (head if isinstance(head, list) else [head]) + (tail if isinstance(tail, list) else [tail])
			for headOrTail in headsAndTails:
				if abs(float(headOrTail.x) - xLowerBoundary) < SPAresabs: internalPortOnXLowerBoundary = True
				if abs(float(headOrTail.x) - xUpperBoundary) < SPAresabs: internalPortOnXUpperBoundary = True
				if abs(float(headOrTail.y) - yLowerBoundary) < SPAresabs: internalPortOnYLowerBoundary = True
				if abs(float(headOrTail.y) - yUpperBoundary) < SPAresabs: internalPortOnYUpperBoundary = True
				if abs(float(headOrTail.z) - zLowerBoundary) < SPAresabs: internalPortOnZLowerBoundary = True
				if abs(float(headOrTail.z) - zUpperBoundary) < SPAresabs: internalPortOnZUpperBoundary = True
		if includeInvalidPorts:
			head=V("(0.0675005) - (0)","(0.030607) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			tail=V("(0.0675005) - (0)","(0.030607) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			extent=None
			port = self._create_internal_port("U3_7","50 ohm Voltage Source",head,tail,extent)
			portShortcutGroups.append((0,port))
			ports.append(port)
			self._set_extra_port_info(port, "inputOutput", 48, "U3_7", "Direct")
			headsAndTails = (head if isinstance(head, list) else [head]) + (tail if isinstance(tail, list) else [tail])
			for headOrTail in headsAndTails:
				if abs(float(headOrTail.x) - xLowerBoundary) < SPAresabs: internalPortOnXLowerBoundary = True
				if abs(float(headOrTail.x) - xUpperBoundary) < SPAresabs: internalPortOnXUpperBoundary = True
				if abs(float(headOrTail.y) - yLowerBoundary) < SPAresabs: internalPortOnYLowerBoundary = True
				if abs(float(headOrTail.y) - yUpperBoundary) < SPAresabs: internalPortOnYUpperBoundary = True
				if abs(float(headOrTail.z) - zLowerBoundary) < SPAresabs: internalPortOnZLowerBoundary = True
				if abs(float(headOrTail.z) - zUpperBoundary) < SPAresabs: internalPortOnZUpperBoundary = True
		if includeInvalidPorts:
			head=V("(0.0675005) - (0)","(0.029337) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			tail=V("(0.0675005) - (0)","(0.029337) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			extent=None
			port = self._create_internal_port("U3_8","50 ohm Voltage Source",head,tail,extent)
			portShortcutGroups.append((0,port))
			ports.append(port)
			self._set_extra_port_info(port, "inputOutput", 49, "U3_8", "Direct")
			headsAndTails = (head if isinstance(head, list) else [head]) + (tail if isinstance(tail, list) else [tail])
			for headOrTail in headsAndTails:
				if abs(float(headOrTail.x) - xLowerBoundary) < SPAresabs: internalPortOnXLowerBoundary = True
				if abs(float(headOrTail.x) - xUpperBoundary) < SPAresabs: internalPortOnXUpperBoundary = True
				if abs(float(headOrTail.y) - yLowerBoundary) < SPAresabs: internalPortOnYLowerBoundary = True
				if abs(float(headOrTail.y) - yUpperBoundary) < SPAresabs: internalPortOnYUpperBoundary = True
				if abs(float(headOrTail.z) - zLowerBoundary) < SPAresabs: internalPortOnZLowerBoundary = True
				if abs(float(headOrTail.z) - zUpperBoundary) < SPAresabs: internalPortOnZUpperBoundary = True
		if includeInvalidPorts:
			head=V("(0.0675005) - (0)","(0.028067) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			tail=V("(0.0675005) - (0)","(0.028067) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			extent=None
			port = self._create_internal_port("U3_9","50 ohm Voltage Source",head,tail,extent)
			portShortcutGroups.append((0,port))
			ports.append(port)
			self._set_extra_port_info(port, "inputOutput", 50, "U3_9", "Direct")
			headsAndTails = (head if isinstance(head, list) else [head]) + (tail if isinstance(tail, list) else [tail])
			for headOrTail in headsAndTails:
				if abs(float(headOrTail.x) - xLowerBoundary) < SPAresabs: internalPortOnXLowerBoundary = True
				if abs(float(headOrTail.x) - xUpperBoundary) < SPAresabs: internalPortOnXUpperBoundary = True
				if abs(float(headOrTail.y) - yLowerBoundary) < SPAresabs: internalPortOnYLowerBoundary = True
				if abs(float(headOrTail.y) - yUpperBoundary) < SPAresabs: internalPortOnYUpperBoundary = True
				if abs(float(headOrTail.z) - zLowerBoundary) < SPAresabs: internalPortOnZLowerBoundary = True
				if abs(float(headOrTail.z) - zUpperBoundary) < SPAresabs: internalPortOnZUpperBoundary = True
		if includeInvalidPorts:
			head=V("(0.067538501) - (0)","(0.026797) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			tail=V("(0.067538501) - (0)","(0.026797) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			extent=None
			port = self._create_internal_port("U3_10","50 ohm Voltage Source",head,tail,extent)
			portShortcutGroups.append((7,port))
			ports.append(port)
			self._set_extra_port_info(port, "inputOutput", 51, "U3_10", "Direct")
			headsAndTails = (head if isinstance(head, list) else [head]) + (tail if isinstance(tail, list) else [tail])
			for headOrTail in headsAndTails:
				if abs(float(headOrTail.x) - xLowerBoundary) < SPAresabs: internalPortOnXLowerBoundary = True
				if abs(float(headOrTail.x) - xUpperBoundary) < SPAresabs: internalPortOnXUpperBoundary = True
				if abs(float(headOrTail.y) - yLowerBoundary) < SPAresabs: internalPortOnYLowerBoundary = True
				if abs(float(headOrTail.y) - yUpperBoundary) < SPAresabs: internalPortOnYUpperBoundary = True
				if abs(float(headOrTail.z) - zLowerBoundary) < SPAresabs: internalPortOnZLowerBoundary = True
				if abs(float(headOrTail.z) - zUpperBoundary) < SPAresabs: internalPortOnZUpperBoundary = True
		if includeInvalidPorts:
			head=V("(0.064516) - (0)","(0.029337) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			tail=V("(0.064516) - (0)","(0.029337) - (0)","(((mask_bottom_layer_Zmax) + (mask_bottom_layer_Zmin)) / (2)) - (0)")
			extent=None
			port = self._create_internal_port("U3_11","50 ohm Voltage Source",head,tail,extent)
			portShortcutGroups.append((0,port))
			ports.append(port)
			self._set_extra_port_info(port, "inputOutput", 52, "U3_11", "Direct")
			headsAndTails = (head if isinstance(head, list) else [head]) + (tail if isinstance(tail, list) else [tail])
			for headOrTail in headsAndTails:
				if abs(float(headOrTail.x) - xLowerBoundary) < SPAresabs: internalPortOnXLowerBoundary = True
				if abs(float(headOrTail.x) - xUpperBoundary) < SPAresabs: internalPortOnXUpperBoundary = True
				if abs(float(headOrTail.y) - yLowerBoundary) < SPAresabs: internalPortOnYLowerBoundary = True
				if abs(float(headOrTail.y) - yUpperBoundary) < SPAresabs: internalPortOnYUpperBoundary = True
				if abs(float(headOrTail.z) - zLowerBoundary) < SPAresabs: internalPortOnZLowerBoundary = True
				if abs(float(headOrTail.z) - zUpperBoundary) < SPAresabs: internalPortOnZUpperBoundary = True
		setPortNbToNameMappingInitialized()
		try:
			if getSessionVersion(self.session) >= 5:
				self.session.appendPortList(ports,None,portShortcutGroups)
			else:
				self.session.appendPortList(ports,self.groupList,portShortcutGroups)
		except AttributeError:
			empro.activeProject.circuitComponents().appendList(ports)
			for group,port in portShortcutGroups:
				self.addShortcut(group,port)
		for i in waveguides.keys():
			empro.activeProject.waveGuides.append(waveguides[i])
		assembly.name="waveguide_planes"
		self.session.hide_part(assembly)

	def create_grid_regions(self):
		gG = empro.activeProject.gridGenerator

	def create_parameters(self):
		self._create_parameter("stack_Antenna_layer_1_Z", "0 um", "Z of topology level (level 1 of stack Antenna)",True,fixGridAxis='Z')
		self._create_parameter("stack_Antenna_layer_3_Z", "35.001 um", "Z of topology level (level 3 of stack Antenna)",True,fixGridAxis='Z')
		self._create_parameter("stack_Antenna_layer_5_Z", "701.041 um", "Z of topology level (level 5 of stack Antenna)",True,fixGridAxis='Z')
		self._create_parameter("stack_Antenna_layer_7_Z", "736.042 um", "Z of topology level (level 7 of stack Antenna)",True,fixGridAxis='Z')
		self._create_parameter("lateralExtension","3000 um","Substrate LATERAL extension", True)
		self._create_parameter("verticalExtension","3000 um","Substrate VERTICAL extension", True)
		self._create_parameter("xLowerExtension", "lateralExtension", "Lower X extension", True)
		self._create_parameter("xUpperExtension", "lateralExtension", "Upper X extension", True)
		self._create_parameter("yLowerExtension", "lateralExtension", "Lower Y extension", True)
		self._create_parameter("yUpperExtension", "lateralExtension", "Upper Y extension", True)
		self._create_parameter("zLowerExtension", "verticalExtension", "Lower Z extension", True)
		self._create_parameter("zUpperExtension", "verticalExtension", "Upper Z extension", True)
		if get_ads_import_version() >= 11 :
			self._create_parameter("toggleExtensionToBoundingBox", 0, "toggle extension of gnd/substrate layers to bounding box of geometry", True)
			self._create_parameter("xLowerBoundingBox", 0.0, "lower X coordinate of bounding box of geometry (for extension of covers)", True)
			self._create_parameter("yLowerBoundingBox", 0.0, "lower Y coordinate of bounding box of geometry (for extension of covers)", True)
			self._create_parameter("zLowerBoundingBox", 0.0, "lower Z coordinate of bounding box of geometry (for extension of covers)", True)
			self._create_parameter("xUpperBoundingBox", 0.0, "upper X coordinate of bounding box of geometry (for extension of covers)", True)
			self._create_parameter("yUpperBoundingBox", 0.0, "upper Y coordinate of bounding box of geometry (for extension of covers)", True)
			self._create_parameter("zUpperBoundingBox", 0.0, "upper Z coordinate of bounding box of geometry (for extension of covers)", True)
		self._create_parameter("mask_bottom_layer_Zmin",str("0 um"),"Zmin of mask bottom_layer",True,fixGridAxis='Z')
		self._create_parameter("mask_bottom_layer_Zmax",str("35.001 um"),"Zmax of mask bottom_layer",True,fixGridAxis='Z')
		self._create_parameter("mask_top_layer_Zmin",str("701.041 um"),"Zmin of mask top_layer",True,fixGridAxis='Z')
		self._create_parameter("mask_top_layer_Zmax",str("736.042 um"),"Zmax of mask top_layer",True,fixGridAxis='Z')
		self._create_parameter("mask_drill_plated_bottom_top_Zmin",str("35.001 um"),"Zmin of mask drill_plated_bottom_top",True,fixGridAxis='Z')
		self._create_parameter("mask_drill_plated_bottom_top_Zmax",str("701.041 um"),"Zmax of mask drill_plated_bottom_top",True,fixGridAxis='Z')

def maxNbThreadsADS():
	maxNbThreads=0
	return maxNbThreads


g_portNbToName={}
g_portNbToNameInitialized=False

def portNbToName():
	if g_portNbToNameInitialized == True:
		return g_portNbToName
	raise RuntimeError("portNbToName used uninitialized")

def setPortNbToNameMappingInitialized( state = True ):
	global g_portNbToNameInitialized
	g_portNbToNameInitialized = True

def radiationPossible():
	return True

def main():
	try:
		demoMode=empro.toolkit.ads_import.useDemoMode()
	except AttributeError:
		demoMode=False
	try:
		ads_import(demoMode=demoMode)
	except Exception:
		empro.toolkit.ads_import.notify_failure()
		raise

if __name__=="__main__":
	main()
	del ads_import
