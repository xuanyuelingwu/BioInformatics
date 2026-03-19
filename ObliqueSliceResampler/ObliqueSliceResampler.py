#!/usr/bin/env python3
"""
ObliqueSliceResampler: A 3D Slicer Python scripted module for MRI oblique plane slicing.

This module allows users to define a custom axis by selecting two fiducial points,
and generates a series of resampled slices perpendicular to this axis.

Author: 鲁奥晗
Student ID: 2023012411
License: MIT
"""

import os
import sys
import math
import numpy as np
from typing import Tuple

import vtk
import slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin


# =============================================================================
# Module Class
# =============================================================================

class ObliqueSliceResampler(ScriptedLoadableModule):
    """
    Main module class for ObliqueSliceResampler.
    This class is responsible for module registration and metadata.
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "Oblique Slice Resampler"
        self.parent.categories = ["Utilities"]
        self.parent.dependencies = []
        self.parent.contributors = ["鲁奥晗 (2023012411)"]
        self.parent.helpText = """
        <p>This module generates resampled MRI slices along a custom axis defined by two fiducial points.</p>
        <p>It is useful for examining pathology along specific anatomical directions,
        for example, perpendicular to the right central sulcus.</p>
        <p><b>Usage:</b></p>
        <ol>
          <li>Load an MRI volume.</li>
          <li>Create a Fiducial list with exactly 2 points to define the custom axis.</li>
          <li>Select the input volume and fiducial list in the module panel.</li>
          <li>Set the desired slice spacing and number of slices.</li>
          <li>Click "Generate Slices" to create the resampled output volume.</li>
        </ol>
        """
        self.parent.acknowledgementText = "Developed using 3D Slicer, VTK, and Python."


# =============================================================================
# Widget Class (UI)
# =============================================================================

class ObliqueSliceResamplerWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
    """
    Widget class for the ObliqueSliceResampler module.
    Handles all user interface elements and interactions.
    """

    def __init__(self, parent=None):
        """Called when the user opens the module the first time and the widget is initialized."""
        ScriptedLoadableModuleWidget.__init__(self, parent)
        VTKObservationMixin.__init__(self)
        self.logic = None

    def setup(self):
        """Called when the user opens the module the first time and the widget is initialized."""
        ScriptedLoadableModuleWidget.setup(self)

        # Create the logic object
        self.logic = ObliqueSliceResamplerLogic()

        # ===== Input Section =====
        import ctk
        inputCollapsibleButton = ctk.ctkCollapsibleButton()
        inputCollapsibleButton.text = "Input"
        self.layout.addWidget(inputCollapsibleButton)
        inputFormLayout = qt.QFormLayout(inputCollapsibleButton)

        # Input Volume Selector
        self.inputVolumeSelector = slicer.qMRMLNodeComboBox()
        self.inputVolumeSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
        self.inputVolumeSelector.selectNodeUponCreation = True
        self.inputVolumeSelector.addEnabled = False
        self.inputVolumeSelector.removeEnabled = False
        self.inputVolumeSelector.noneEnabled = False
        self.inputVolumeSelector.showHidden = False
        self.inputVolumeSelector.showChildNodeTypes = False
        self.inputVolumeSelector.setMRMLScene(slicer.mrmlScene)
        self.inputVolumeSelector.setToolTip("Select the input MRI volume")
        inputFormLayout.addRow("Input Volume: ", self.inputVolumeSelector)

        # Fiducial Selector
        self.fiducialSelector = slicer.qMRMLNodeComboBox()
        self.fiducialSelector.nodeTypes = ["vtkMRMLMarkupsFiducialNode"]
        self.fiducialSelector.selectNodeUponCreation = False
        self.fiducialSelector.addEnabled = False
        self.fiducialSelector.removeEnabled = False
        self.fiducialSelector.noneEnabled = False
        self.fiducialSelector.showHidden = False
        self.fiducialSelector.showChildNodeTypes = False
        self.fiducialSelector.setMRMLScene(slicer.mrmlScene)
        self.fiducialSelector.setToolTip(
            "Select a Fiducial list with exactly 2 points defining the custom axis"
        )
        inputFormLayout.addRow("Axis Fiducials (2 pts): ", self.fiducialSelector)

        # ===== Parameters Section =====
        parametersCollapsibleButton = ctk.ctkCollapsibleButton()
        parametersCollapsibleButton.text = "Parameters"
        parametersCollapsibleButton.collapsed = False
        self.layout.addWidget(parametersCollapsibleButton)
        parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

        # Slice Spacing
        self.sliceSpacingSpinBox = qt.QDoubleSpinBox()
        self.sliceSpacingSpinBox.minimum = 0.1
        self.sliceSpacingSpinBox.maximum = 100.0
        self.sliceSpacingSpinBox.value = 2.0
        self.sliceSpacingSpinBox.singleStep = 0.5
        self.sliceSpacingSpinBox.setToolTip("Spacing between consecutive slices in mm")
        parametersFormLayout.addRow("Slice Spacing (mm): ", self.sliceSpacingSpinBox)

        # Number of Slices
        self.numSlicesSpinBox = qt.QSpinBox()
        self.numSlicesSpinBox.minimum = 1
        self.numSlicesSpinBox.maximum = 500
        self.numSlicesSpinBox.value = 50
        self.numSlicesSpinBox.singleStep = 1
        self.numSlicesSpinBox.setToolTip("Number of slices to generate")
        parametersFormLayout.addRow("Number of Slices: ", self.numSlicesSpinBox)

        # Output Volume Name
        self.outputVolumeLineEdit = qt.QLineEdit()
        self.outputVolumeLineEdit.setText("ObliqueSlices")
        self.outputVolumeLineEdit.setToolTip("Name for the output resampled volume")
        parametersFormLayout.addRow("Output Volume Name: ", self.outputVolumeLineEdit)

        # ===== Action Section =====
        actionCollapsibleButton = ctk.ctkCollapsibleButton()
        actionCollapsibleButton.text = "Action"
        actionCollapsibleButton.collapsed = False
        self.layout.addWidget(actionCollapsibleButton)
        actionFormLayout = qt.QFormLayout(actionCollapsibleButton)

        # Generate Slices Button
        self.generateButton = qt.QPushButton("Generate Slices")
        self.generateButton.toolTip = "Generate resampled slices along the custom axis"
        self.generateButton.clicked.connect(self.onGenerateSlices)
        actionFormLayout.addRow(self.generateButton)

        # Add vertical spacer
        self.layout.addStretch(1)

    def cleanup(self):
        """Called when the application closes and the module widget is destroyed."""
        self.removeObservers()

    def onGenerateSlices(self):
        """Handle the Generate Slices button click event."""
        try:
            # Validate: Input Volume
            inputVolume = self.inputVolumeSelector.currentNode()
            if not inputVolume:
                slicer.util.errorDisplay("Please select an input volume.")
                return

            # Validate: Fiducial Points
            fiducialNode = self.fiducialSelector.currentNode()
            if not fiducialNode:
                slicer.util.errorDisplay("Please select a fiducial list.")
                return

            numFiducials = fiducialNode.GetNumberOfFiducials()
            if numFiducials != 2:
                slicer.util.errorDisplay(
                    f"Exactly 2 fiducial points are required to define the axis. "
                    f"Found {numFiducials} point(s)."
                )
                return

            # Get parameters
            sliceSpacing = self.sliceSpacingSpinBox.value
            numSlices = self.numSlicesSpinBox.value
            outputVolumeName = self.outputVolumeLineEdit.text.strip()
            if not outputVolumeName:
                outputVolumeName = "ObliqueSlices"

            # Execute the logic
            self.logic.generateObliqueSlices(
                inputVolume=inputVolume,
                fiducialNode=fiducialNode,
                sliceSpacing=sliceSpacing,
                numSlices=numSlices,
                outputVolumeName=outputVolumeName
            )

            slicer.util.infoDisplay(
                f"Oblique slices generated successfully.\n"
                f"Output volume: '{outputVolumeName}'"
            )

        except Exception as e:
            slicer.util.errorDisplay(f"An error occurred during slice generation:\n{str(e)}")
            import traceback
            traceback.print_exc()


# =============================================================================
# Logic Class (Core Algorithm)
# =============================================================================

class ObliqueSliceResamplerLogic(ScriptedLoadableModuleLogic):
    """
    Logic class for the ObliqueSliceResampler module.
    Contains the core algorithm for oblique image resampling.
    This class is independent of the UI and can be used in scripts.
    """

    def generateObliqueSlices(
        self,
        inputVolume,
        fiducialNode,
        sliceSpacing: float,
        numSlices: int,
        outputVolumeName: str
    ):
        """
        Generate resampled slices along a custom axis defined by two fiducial points.

        The axis is defined by two points P1 and P2 in RAS coordinates.
        Each output slice is a plane perpendicular to the P1->P2 axis vector,
        spaced `sliceSpacing` mm apart, starting from P1.

        Args:
            inputVolume: Input MRI volume (vtkMRMLScalarVolumeNode).
            fiducialNode: Fiducial list with exactly 2 points (vtkMRMLMarkupsFiducialNode).
            sliceSpacing: Distance between consecutive slices in mm.
            numSlices: Total number of slices to generate.
            outputVolumeName: Name for the new output volume node.

        Returns:
            The created output volume node (vtkMRMLScalarVolumeNode).
        """
        # --- Step 1: Extract fiducial coordinates (RAS) ---
        p1_ras = np.zeros(3)
        p2_ras = np.zeros(3)
        fiducialNode.GetNthFiducialPosition(0, p1_ras)
        fiducialNode.GetNthFiducialPosition(1, p2_ras)

        print(f"[ObliqueSliceResampler] P1 (RAS): {p1_ras}")
        print(f"[ObliqueSliceResampler] P2 (RAS): {p2_ras}")

        # --- Step 2: Compute and normalize the axis vector ---
        axisVector = p2_ras - p1_ras
        axisLength = np.linalg.norm(axisVector)
        if axisLength < 1e-6:
            raise ValueError(
                "The two fiducial points are too close together. "
                "Please select two distinct anatomical landmarks."
            )
        axisNorm = axisVector / axisLength
        print(f"[ObliqueSliceResampler] Axis unit vector: {axisNorm}")

        # --- Step 3: Compute orthogonal in-plane basis vectors ---
        # xDir and yDir span the plane perpendicular to the axis.
        xDir, yDir = self._computeOrthogonalBasis(axisNorm)
        print(f"[ObliqueSliceResampler] X-dir: {xDir}, Y-dir: {yDir}")

        # --- Step 4: Determine output volume dimensions ---
        inputImageData = inputVolume.GetImageData()
        inputSpacing = np.array(inputVolume.GetSpacing())
        inputExtent = inputImageData.GetExtent()

        # Preserve the in-plane resolution of the input volume
        outWidth = inputExtent[1] - inputExtent[0] + 1
        outHeight = inputExtent[3] - inputExtent[2] + 1
        outputExtent = [0, outWidth - 1, 0, outHeight - 1, 0, numSlices - 1]

        # --- Step 5: Build the reslice transformation matrix ---
        # This 4x4 matrix maps output voxel coordinates to RAS world coordinates.
        resliceAxes = self._buildResliceMatrix(p1_ras, xDir, yDir, axisNorm)

        # --- Step 6: Perform image resampling with vtkImageReslice ---
        reslice = vtk.vtkImageReslice()
        reslice.SetInputData(inputImageData)
        reslice.SetResliceAxes(resliceAxes)
        reslice.SetOutputSpacing(inputSpacing[0], inputSpacing[1], sliceSpacing)
        reslice.SetOutputExtent(outputExtent)
        reslice.SetInterpolationModeToLinear()
        reslice.SetBackgroundLevel(0)
        reslice.Update()

        outputImageData = reslice.GetOutput()

        # --- Step 7: Create and configure the output MRML volume node ---
        outputVolume = slicer.mrmlScene.AddNewNodeByClass(
            "vtkMRMLScalarVolumeNode", outputVolumeName
        )
        outputVolume.SetAndObserveImageData(outputImageData)

        # Set the IJK-to-RAS transform so Slicer knows where the volume is in space
        ijkToRasMatrix = vtk.vtkMatrix4x4()
        ijkToRasMatrix.DeepCopy(resliceAxes)
        ijkToRasMatrix.Invert()
        outputVolume.SetIJKToRASMatrix(ijkToRasMatrix)

        # Copy display settings from the input volume
        inputDisplayNode = inputVolume.GetDisplayNode()
        if inputDisplayNode:
            outputVolume.CreateDefaultDisplayNodes()
            outputDisplayNode = outputVolume.GetDisplayNode()
            if outputDisplayNode:
                outputDisplayNode.SetAndObserveColorNodeID(
                    inputDisplayNode.GetColorNodeID()
                )
                outputDisplayNode.SetWindow(inputDisplayNode.GetWindow())
                outputDisplayNode.SetLevel(inputDisplayNode.GetLevel())

        # Update the slice viewers to show the new volume
        slicer.util.setSliceViewerLayers(background=outputVolume)

        print(
            f"[ObliqueSliceResampler] Output volume '{outputVolumeName}' "
            f"created with {numSlices} slices at {sliceSpacing} mm spacing."
        )
        return outputVolume

    @staticmethod
    def _computeOrthogonalBasis(normal: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute two orthogonal unit vectors that span the plane perpendicular to `normal`.

        Uses the Gram-Schmidt process to find a stable orthogonal basis.

        Args:
            normal: A unit vector defining the plane's normal direction.

        Returns:
            A tuple (xDir, yDir) of two orthogonal unit vectors.
        """
        # Choose a reference vector not parallel to the normal
        if abs(normal[0]) < 0.9:
            reference = np.array([1.0, 0.0, 0.0])
        else:
            reference = np.array([0.0, 1.0, 0.0])

        # Gram-Schmidt: first basis vector
        xDir = reference - np.dot(reference, normal) * normal
        xDir = xDir / np.linalg.norm(xDir)

        # Second basis vector via cross product (guaranteed orthogonal)
        yDir = np.cross(normal, xDir)
        yDir = yDir / np.linalg.norm(yDir)

        return xDir, yDir

    @staticmethod
    def _buildResliceMatrix(
        origin: np.ndarray,
        xDir: np.ndarray,
        yDir: np.ndarray,
        zDir: np.ndarray
    ) -> vtk.vtkMatrix4x4:
        """
        Build a 4x4 VTK matrix for use with vtkImageReslice.

        The matrix encodes the orientation and origin of the output volume
        in RAS world coordinates. Columns represent the X, Y, Z axes and
        the translation (origin).

        Args:
            origin: The origin point of the output volume in RAS coordinates.
            xDir: Unit vector for the output volume's X axis.
            yDir: Unit vector for the output volume's Y axis.
            zDir: Unit vector for the output volume's Z axis (slice normal).

        Returns:
            A vtkMatrix4x4 suitable for vtkImageReslice.SetResliceAxes().
        """
        matrix = vtk.vtkMatrix4x4()
        matrix.Identity()

        # Column 0: X axis direction
        matrix.SetElement(0, 0, xDir[0])
        matrix.SetElement(1, 0, xDir[1])
        matrix.SetElement(2, 0, xDir[2])

        # Column 1: Y axis direction
        matrix.SetElement(0, 1, yDir[0])
        matrix.SetElement(1, 1, yDir[1])
        matrix.SetElement(2, 1, yDir[2])

        # Column 2: Z axis direction (slice normal = custom axis)
        matrix.SetElement(0, 2, zDir[0])
        matrix.SetElement(1, 2, zDir[1])
        matrix.SetElement(2, 2, zDir[2])

        # Column 3: Origin (translation)
        matrix.SetElement(0, 3, origin[0])
        matrix.SetElement(1, 3, origin[1])
        matrix.SetElement(2, 3, origin[2])

        return matrix


# =============================================================================
# Test Class
# =============================================================================

class ObliqueSliceResamplerTest(ScriptedLoadableModuleTest):
    """
    Test class for ObliqueSliceResampler.
    Tests are run by selecting "Reload and Test" in the module panel,
    or via Edit -> Run Tests.
    """

    def setUp(self):
        """Reset the scene before each test."""
        slicer.mrmlScene.Clear()

    def runTest(self):
        """Run all tests."""
        self.setUp()
        self.test_orthogonalBasis()
        self.test_resliceMatrix()
        self.test_fullPipeline()

    def test_orthogonalBasis(self):
        """Test that the computed basis vectors are orthogonal and unit length."""
        self.delayDisplay("Testing orthogonal basis computation...")

        logic = ObliqueSliceResamplerLogic()
        normal = np.array([0.0, 0.0, 1.0])
        xDir, yDir = logic._computeOrthogonalBasis(normal)

        # Check unit length
        self.assertAlmostEqual(np.linalg.norm(xDir), 1.0, places=6)
        self.assertAlmostEqual(np.linalg.norm(yDir), 1.0, places=6)

        # Check orthogonality
        self.assertAlmostEqual(np.dot(xDir, yDir), 0.0, places=6)
        self.assertAlmostEqual(np.dot(xDir, normal), 0.0, places=6)
        self.assertAlmostEqual(np.dot(yDir, normal), 0.0, places=6)

        self.delayDisplay("test_orthogonalBasis PASSED")

    def test_resliceMatrix(self):
        """Test that the reslice matrix is correctly constructed."""
        self.delayDisplay("Testing reslice matrix construction...")

        logic = ObliqueSliceResamplerLogic()
        origin = np.array([10.0, 20.0, 30.0])
        xDir = np.array([1.0, 0.0, 0.0])
        yDir = np.array([0.0, 1.0, 0.0])
        zDir = np.array([0.0, 0.0, 1.0])

        matrix = logic._buildResliceMatrix(origin, xDir, yDir, zDir)

        self.assertAlmostEqual(matrix.GetElement(0, 3), 10.0, places=6)
        self.assertAlmostEqual(matrix.GetElement(1, 3), 20.0, places=6)
        self.assertAlmostEqual(matrix.GetElement(2, 3), 30.0, places=6)
        self.assertAlmostEqual(matrix.GetElement(0, 0), 1.0, places=6)

        self.delayDisplay("test_resliceMatrix PASSED")

    def test_fullPipeline(self):
        """Test the full slice generation pipeline with a synthetic volume."""
        self.delayDisplay("Testing full pipeline with synthetic data...")

        # Create a synthetic 64x64x64 volume
        imageData = vtk.vtkImageData()
        imageData.SetDimensions(64, 64, 64)
        imageData.SetSpacing(1.0, 1.0, 1.0)
        imageData.AllocateScalars(vtk.VTK_SHORT, 1)
        imageData.GetPointData().GetScalars().Fill(100)

        inputVolume = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode", "TestInput")
        inputVolume.SetAndObserveImageData(imageData)
        inputVolume.CreateDefaultDisplayNodes()

        # Create fiducial points
        fiducialNode = slicer.mrmlScene.AddNewNodeByClass(
            "vtkMRMLMarkupsFiducialNode", "TestAxis"
        )
        fiducialNode.AddFiducial(0.0, 0.0, 0.0)
        fiducialNode.AddFiducial(0.0, 0.0, 30.0)

        # Run the logic
        logic = ObliqueSliceResamplerLogic()
        outputVolume = logic.generateObliqueSlices(
            inputVolume=inputVolume,
            fiducialNode=fiducialNode,
            sliceSpacing=2.0,
            numSlices=10,
            outputVolumeName="TestOutput"
        )

        self.assertIsNotNone(outputVolume)
        outputImageData = outputVolume.GetImageData()
        self.assertIsNotNone(outputImageData)
        dims = outputImageData.GetDimensions()
        self.assertEqual(dims[2], 10)

        self.delayDisplay("test_fullPipeline PASSED")
