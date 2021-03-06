import maya.cmds as mc
from maya import OpenMaya

class armIkFkBlending():
	def __init__(self):
		self.blendedJoints = []
		self.fkJoints = []
		self.jointNames = []
		self.ikJoints = []
		self.ikControls = []
		self.fkControls = []
		self.fkControlGroups = []

		joint1= mc.ls(sl = True)[0]
		joint2 = mc.listRelatives(joint1, children = True)[0]
		joint3 = mc.listRelatives(joint2, children = True)[0]

		for joint in [joint1, joint2, joint3]:
			self.blendedJoints.append(joint)

		self.jointNames.append(joint1.rpartition("_")[0])
		self.jointNames.append(joint2.rpartition("_")[0])
		self.jointNames.append(joint3.rpartition("_")[0])

		ikJoint1 = mc.duplicate(joint1, n = self.jointNames[0]+"_IK_JNT", renameChildren = True)[0]
		ikJoint2 = mc.rename(mc.listRelatives(ikJoint1, children = True)[0], self.jointNames[1]+"_IK_JNT")
		ikJoint3 = mc.rename(mc.listRelatives(ikJoint2, children = True)[0], self.jointNames[2]+"_IK_JNT")

		for joint in [ikJoint1, ikJoint2, ikJoint3]:
			self.ikJoints.append(joint)

		fkJoint1 = mc.duplicate(joint1, n = self.jointNames[0]+"_FK_JNT", renameChildren = True)[0]
		fkJoint2 = mc.rename(mc.listRelatives(fkJoint1, children = True)[0], self.jointNames[1]+"_FK_JNT")
		fkJoint3 = mc.rename(mc.listRelatives(fkJoint2, children = True)[0], self.jointNames[2]+"_FK_JNT")

		for joint in [fkJoint1, fkJoint2, fkJoint3]:
			self.fkJoints.append(joint)

		self.createFKControl()
		self.createIKControl()

		self.blend()

		self.mainGroup = mc.group(self.fkJoints[0], self.ikJoints[0], self.blendedJoints[0], n = joint1+"_GRP")

	def createFKControl(self):
		for joint in self.fkJoints:
			control = self.generateFKControl()
			controlName = joint.rpartition("_")[0] + "_CTL"
			FKControlObject = mc.rename(control, controlName)
			self.fkControls.append(FKControlObject)
			FKControlObjectShapes = mc.listRelatives(FKControlObject, children = True)
			mc.parent(FKControlObject, joint, relative = True)
			mc.makeIdentity(FKControlObject)
			mc.parent(FKControlObject, world = True)
			for shape in FKControlObjectShapes:
				mc.parent(shape, joint, relative = True, shape = True)

	def generateFKControl(self):
		circle1 = mc.listRelatives(mc.circle( nr=(1, 0, 0), c=(0, 0, 0), r = 2)[0], children = True)[0]
		mc.setAttr(circle1+".overrideEnabled", 1)
		mc.setAttr(circle1+".overrideColor", 13)
		circle2 = mc.listRelatives(mc.circle( nr=(0, 1, 0), c=(0, 0, 0), r = 2)[0], children = True)[0]
		mc.setAttr(circle2+".overrideEnabled", 1)
		mc.setAttr(circle2+".overrideColor", 13)
		circle3 = mc.listRelatives(mc.circle( nr=(0, 0, 1), c=(0, 0, 0), r = 2)[0], children = True)[0]
		mc.setAttr(circle3+".overrideEnabled", 1)
		mc.setAttr(circle3+".overrideColor", 13)
		groupName = mc.group(empty = True, n = "fkControl")
		mc.parent(circle1, groupName, relative = True, shape = True)
		mc.parent(circle2, groupName, relative = True, shape = True)
		mc.parent(circle3, groupName, relative = True, shape = True)
		return groupName

	def createIKControl(self):
		joint1Pos = mc.xform(self.ikJoints[0], q = True, ws = True, t = True)
		joint2Pos = mc.xform(self.ikJoints[1], q = True, ws = True, t = True)
		joint3Pos = mc.xform(self.ikJoints[2], q = True, ws = True, t = True)

		startV = OpenMaya.MVector(joint1Pos[0] ,joint1Pos[1],joint1Pos[2])
		midV = OpenMaya.MVector(joint2Pos[0] ,joint2Pos[1],joint2Pos[2])
		endV = OpenMaya.MVector(joint3Pos[0] ,joint3Pos[1],joint3Pos[2])

		startEnd = endV - startV
		startMid = midV - startV

		dotP = startMid * startEnd

		proj = float(dotP) / float(startEnd.length())

		startEndN = startEnd.normal()

		projV = startEndN * proj

		arrowV = startMid - projV

		arrowV*= 10

		finalV = arrowV + midV

		poleVectorControl = mc.spaceLocator(n = self.jointNames[1] + "_PV_CTL")[0]

		mc.xform(poleVectorControl , ws =1 , t= (finalV.x , finalV.y ,finalV.z))
		mc.makeIdentity(poleVectorControl, apply=True, t=1, r=1, s=1, n=0)

		ikHandle = mc.ikHandle(sj = self.ikJoints[0], ee = self.ikJoints[2], sol = "ikRPsolver")[0]

		self.ikControlObject = mc.circle(nr = (0, 0, 1), c = (0,0,0), r = 10, name = self.jointNames[2]+"_IK_CTL")[0]

		# mc.xform(self.ikControlObject, worldSpace=True, translation=mc.xform(self.ikJoints[2], query = True, worldSpace = True, translation = True))

		mc.makeIdentity(self.ikControlObject, apply=True, t=1, r=1, s=1, n=0)

		ikControlOffsetGroup = mc.group(self.ikControlObject, n = self.ikControlObject.replace('_CTL', 'Offset_GRP'))
		ikControlGroup = mc.group(ikControlOffsetGroup, n = self.ikControlObject.replace('_CTL', '_GRP'))

		mc.parent(ikControlGroup, self.ikJoints[2])
		mc.makeIdentity(ikControlGroup, t = 1, r = 1, s = 1)
		mc.parent(ikControlGroup, world=True)
		mc.orientConstraint(self.ikControlObject, self.ikJoints[2], mo=False)

		mc.parent(ikHandle, self.ikControlObject)

		poleVector = mc.poleVectorConstraint(poleVectorControl, ikHandle)

		self.ikControls.append(self.ikControlObject)
		self.ikControls.append(poleVectorControl)

	def blend(self):
		self.blendColor1 = mc.shadingNode("blendColors", asUtility = True, n = self.blendedJoints[0].rpartition("_")[0]+"_BLC")
		self.blendColor2 = mc.shadingNode("blendColors", asUtility = True, n = self.blendedJoints[1].rpartition("_")[0]+"_BLC")
		self.blendColor3 = mc.shadingNode("blendColors", asUtility = True, n = self.blendedJoints[2].rpartition("_")[0]+"_BLC")

		self.mainControl = mc.circle(nr = (0, 1, 0), c = (0,0,0), r = 3)[0]

		mc.addAttr(self.mainControl, ln = "ik_fk_blend", attributeType = "float", minValue = 0.00, maxValue = 1.00, keyable = True)

		mc.connectAttr(self.ikJoints[0]+".rotate", self.blendColor1+".color1")
		
		mc.connectAttr(self.fkJoints[0]+".rotate", self.blendColor1+".color2")
		
		mc.connectAttr(self.mainControl+".ik_fk_blend", self.blendColor1+".blender")

		mc.connectAttr(self.blendColor1+".output", self.blendedJoints[0]+".rotate")
		
		mc.connectAttr(self.ikJoints[1]+".rotate", self.blendColor2+".color1")
		
		mc.connectAttr(self.fkJoints[1]+".rotate", self.blendColor2+".color2")
		
		mc.connectAttr(self.mainControl+".ik_fk_blend", self.blendColor2+".blender")

		mc.connectAttr(self.blendColor2+".output", self.blendedJoints[1]+".rotate")

		mc.connectAttr(self.ikJoints[2]+".rotate", self.blendColor3+".color1")
		
		mc.connectAttr(self.fkJoints[2]+".rotate", self.blendColor3+".color2")
		
		mc.connectAttr(self.mainControl+".ik_fk_blend", self.blendColor3+".blender")

		mc.connectAttr(self.blendColor3+".output", self.blendedJoints[2]+".rotate")

		self.reverseNode1 = mc.shadingNode("reverse", asUtility = True, n = self.blendedJoints[0].rpartition("_")[0]+"_REV")

		mc.connectAttr(self.mainControl+".ik_fk_blend", self.reverseNode1+".input.inputX")

		mc.connectAttr(self.reverseNode1+".outputX", self.fkJoints[0]+".visibility")
		# mc.connectAttr(self.reverseNode1+".outputX", self.fkControls[1]+".visibility")
		# mc.connectAttr(self.reverseNode1+".outputX", self.fkControls[2]+".visibility")

		mc.connectAttr(self.mainControl+".ik_fk_blend", self.ikControls[0]+".visibility")
		mc.connectAttr(self.mainControl+".ik_fk_blend", self.ikControls[1]+".visibility")
		ikControlPos = mc.xform(self.ikControlObject, query = True, worldSpace = True, rp = True)
		self.mainControlPos = [pos + 10 for pos in ikControlPos]
		mc.xform(self.mainControl, worldSpace=True, translation = self.mainControlPos)
		mc.rename(self.mainControl, self.ikControls[0].replace('_CTL', 'Switch_CTL'))


object = armIkFkBlending()