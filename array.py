#! /usr/bin/python

import sys
import os
import math
import datetime
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import ControlWindow
import SceneWindow

class MainControlWindow(QMainWindow, ControlWindow.Ui_ControlWindow):
	
	"""
	This is the main window of the program.
	"""
	
	def __init__(self, parent=None):
		QMainWindow.__init__(self, parent)
		ControlWindow.Ui_ControlWindow.__init__(self, parent)
		
		# Build the main window using the setupUi method generated by Qt Designer
		self.setupUi(self)

		# Start with the "invert" action unchecked
		self.action_invert.setChecked(False)

		# Populate the list of shapes in the Shapes tab
		self.shapes_comboBox.addItems(['Circle', 'Rectangle'])

		# Create the window that will show the scene
		self.sceneWindow = MainSceneWindow(parent=self)
		self.sceneWindow.show()

		# Connections
		#self.connect(self.action_reset, SIGNAL("activated()"), self.sceneWindow.createScene)
		self.connect(self.action_invert, SIGNAL("toggled(bool)"), self.sceneWindow.setColours)
		self.connect(self.shapes_comboBox, SIGNAL("currentIndexChanged(int)"), self.sceneWindow.createScene)
		self.connect(self.aspectRatio_doubleSpinBox, SIGNAL("valueChanged(double)"), self.sceneWindow.setAspectRatio)
		self.connect(self.thickness_spinBox, SIGNAL("valueChanged(int)"), self.sceneWindow.setColours)
		self.connect(self.scale_doubleSpinBox, SIGNAL("valueChanged(double)"), self.sceneWindow.setScale)
		self.connect(self.rotation_doubleSpinBox, SIGNAL("valueChanged(double)"), self.sceneWindow.setRotation)
		self.connect(self.filled_checkBox, SIGNAL("stateChanged(int)"), self.sceneWindow.setColours)
		self.connect(self.grouped_checkBox, SIGNAL("stateChanged(int)"), self.sceneWindow.setGrouping)
		self.connect(self.nrows_spinBox, SIGNAL("valueChanged(int)"), self.sceneWindow.createScene)
		self.connect(self.ncolumns_spinBox, SIGNAL("valueChanged(int)"), self.sceneWindow.createScene)
		self.connect(self.rowPitch_doubleSpinBox, SIGNAL("valueChanged(double)"), self.sceneWindow.setPitch)
		self.connect(self.columnPitch_doubleSpinBox, SIGNAL("valueChanged(double)"), self.sceneWindow.setPitch)
		

class MainSceneWindow(QMainWindow, SceneWindow.Ui_SceneWindow):
	"""
	This is the window that shows the scene
	"""
	
	def __init__(self, parent=None):
		QDialog.__init__(self, parent)
		SceneWindow.Ui_SceneWindow.__init__(self, parent)
		
		# Build the window using the setupUi method generated by Qt Designer
		self.setupUi(self)
		
		# Create the scene and visualize it
		self.createScene()

	def createScene(self):
		"""
		Create the scene
		"""
		
		# Create the scene and set it to be very big so that the QGraphicsView does not pull
		# off its shite about aligning the scene to fit in the view
		self.scene = QGraphicsScene(parent=self)
		self.scene.setSceneRect(-1024/2, -768/2, 1024, 768)

		# Read the parameters set in the interface
		selectedShape = self.parent().shapes_comboBox.currentIndex()
		nrows = self.parent().nrows_spinBox.value()
		ncolumns = self.parent().ncolumns_spinBox.value()
		self.radius = 50 # This is the radius for the circles and half the size for the rectangles
		aspectRatio = self.parent().aspectRatio_doubleSpinBox.value()

		# Create the group that will contain the items
		self.group = QGraphicsItemGroup()
		self.group.setFlags(QGraphicsItem.GraphicsItemFlags(1)) # Make item movable
		self.scene.addItem(self.group)

		# Create the items in the scene
		self.itemList = []
		for row in xrange(nrows):
			for column in xrange(ncolumns):
				if selectedShape == 0:		# Circles selected
					item = QGraphicsEllipseItem(-self.radius*aspectRatio, -self.radius, 2*self.radius*aspectRatio,  2*self.radius)
				elif selectedShape == 1:	# Rectangles selected
					item = QGraphicsRectItem(-self.radius*aspectRatio,  -self.radius,  2*self.radius*aspectRatio, 2*self.radius)
				
				item.setFlags(QGraphicsItem.GraphicsItemFlags(1)) # Make item movable
				self.itemList.append(item)
				self.scene.addItem(item)
		
		# Goup them if required by the corresponding flag
		self.setGrouping()
		
		# Position the items
		self.setPitch()

		# Set the colors of the background and foreground according to the "inverted",
		# "thickness" and "filled" properties
		self.setColours()
		
		# Set the scale and rotation
		self.setScale()
		self.setRotation()
		
		# Display the scene
		self.graphicsView.setScene(self.scene)

	def setGrouping(self):
		"""
		Group or ungroup the items
		"""
	
		grouped = self.parent().grouped_checkBox.isChecked()
		
		if grouped:
			for item in self.itemList:
				self.group.addToGroup(item)
		else:
			for item in self.itemList:
				self.group.removeFromGroup(item)

	def setColours(self):
		"""
		Set the colours and pen thickness according to the "inverted", "filled"
		and "thickness" properties.
		"""

		filled = self.parent().filled_checkBox.isChecked()
		inverted = self.parent().action_invert.isChecked()
		thickness = self.parent().thickness_spinBox.value()
		
		if inverted:
			self.scene.setBackgroundBrush(Qt.white)
			pen = QPen(Qt.black, thickness)
			foregroundBrush = QBrush(Qt.black)
			backgroundBrush = QBrush(Qt.white)
		else:
			self.scene.setBackgroundBrush(Qt.black)
			pen = QPen(Qt.white, thickness)
			foregroundBrush = QBrush(Qt.white)
			backgroundBrush = QBrush(Qt.black)
		
		for item in self.itemList:
			item.setPen(pen)
			if filled:
				item.setBrush(foregroundBrush)
			else:
				item.setBrush(backgroundBrush)

	def setScale(self):
		"""
		Set the scale of the goup or individual items
		"""
		
		scale = self.parent().scale_doubleSpinBox.value()
		grouped = self.parent().grouped_checkBox.isChecked()

		if grouped:
			self.group.setScale(scale)
		else:
			for item in self.itemList:
				item.setScale(scale)
	
	def setRotation(self):
		"""
		Set the rotation of the group or the individual items
		"""
		
		grouped = self.parent().grouped_checkBox.isChecked()
		angle = self.parent().rotation_doubleSpinBox.value()

		if grouped:
			self.group.setRotation(angle)
		else:
			for item in self.itemList:
				item.setRotation(angle)

	def setPitch(self):
		"""
		Set the horizontal and vertical pitch of the array
		"""
		
		row_pitch = self.parent().rowPitch_doubleSpinBox.value()
		column_pitch = self.parent().columnPitch_doubleSpinBox.value()
		nrows = self.parent().nrows_spinBox.value()
		ncolumns = self.parent().ncolumns_spinBox.value()

		row_period = 2 * self.radius + row_pitch
		column_period = 2 * self.radius + column_pitch
		xoffset = ((ncolumns-1) * column_period) / 2.0
		yoffset = ((nrows-1) * row_period) / 2.0
		
		for row in xrange(nrows):
			for column in xrange(ncolumns):
				self.itemList[row*ncolumns + column].setPos(-xoffset + column * column_period, -yoffset + row * row_period)

	def setAspectRatio(self):
		"""
		Set the aspect ratio of the features
		"""
		
		aspectRatio = self.parent().aspectRatio_doubleSpinBox.value()
		for item in self.itemList:
			item.setRect(-self.radius*aspectRatio, -self.radius, 2*self.radius*aspectRatio,  2*self.radius)

		
def main():
	app = QApplication(sys.argv)
	#app.setStyle("plastique")
	controlWin = MainControlWindow()
	controlWin.show()
	app.exec_()

main()
