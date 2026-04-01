#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SurfaceNormalSlicer — 3D Slicer scripted module
================================================
FreeSurfer-guided oblique MRI slice reconstruction.

Author: 鲁奥晗 (2023012411)
License: MIT
"""

# ── Standard library ──────────────────────────────────────────────────────────
import os
import math

# ── Third-party (always available inside Slicer) ──────────────────────────────
import numpy as np
import vtk
import qt
import ctk
import slicer
from slicer.ScriptedLoadableModule import (
    ScriptedLoadableModule,
    ScriptedLoadableModuleWidget,
    ScriptedLoadableModuleLogic,
    ScriptedLoadableModuleTest,
)
from slicer.util import VTKObservationMixin


# =============================================================================
# 1. Module — registration & metadata
# =============================================================================

class SurfaceNormalSlicer(ScriptedLoadableModule):
    """Module metadata.  The class name MUST match the filename stem."""

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title       = "Surface Normal Slicer"
        self.parent.categories  = ["Neuroimaging"]
        self.parent.dependencies = []
        self.parent.contributors = ["Lu Aohan (2023012411)"]
        self.parent.helpText = (
            "<h3>Surface Normal Slicer</h3>"
            "<p>Click any point on a FreeSurfer cortical surface; the selected "
            "2-D slice view is instantly reoriented to the tangent plane at that "
            "point so you can scroll through oblique slices along the surface "
            "normal axis.</p>"
        )
        self.parent.acknowledgementText = (
            "Built with 3D Slicer, VTK and Python. "
            "FreeSurfer surface import via SlicerFreeSurfer extension."
        )


# =============================================================================
# 2. Widget — user interface
# =============================================================================

class SurfaceNormalSlicerWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
    """Qt widget for SurfaceNormalSlicer."""

    def __init__(self, parent=None):
        ScriptedLoadableModuleWidget.__init__(self, parent)
        VTKObservationMixin.__init__(self)
        self.logic = None

    # ------------------------------------------------------------------
    def setup(self):
        ScriptedLoadableModuleWidget.setup(self)
        self.logic = SurfaceNormalSlicerLogic()

        # ── 2-A  Input panel ──────────────────────────────────────────
        inputBox = ctk.ctkCollapsibleButton()
        inputBox.text = "Input"
        self.layout.addWidget(inputBox)
        inputForm = qt.QFormLayout(inputBox)

        # MRI volume
        self.volumeSelector = slicer.qMRMLNodeComboBox()
        self.volumeSelector.nodeTypes           = ["vtkMRMLScalarVolumeNode"]
        self.volumeSelector.selectNodeUponCreation = True
        self.volumeSelector.addEnabled          = False
        self.volumeSelector.removeEnabled       = False
        self.volumeSelector.noneEnabled         = False
        self.volumeSelector.showHidden          = False
        self.volumeSelector.setMRMLScene(slicer.mrmlScene)
        self.volumeSelector.setToolTip("Select the MRI volume (DICOM or NIfTI)")
        inputForm.addRow("MRI Volume:", self.volumeSelector)

        # Cortical surface model
        self.modelSelector = slicer.qMRMLNodeComboBox()
        self.modelSelector.nodeTypes           = ["vtkMRMLModelNode"]
        self.modelSelector.selectNodeUponCreation = False
        self.modelSelector.addEnabled          = False
        self.modelSelector.removeEnabled       = False
        self.modelSelector.noneEnabled         = False
        self.modelSelector.showHidden          = False
        self.modelSelector.setMRMLScene(slicer.mrmlScene)
        self.modelSelector.setToolTip(
            "Select the FreeSurfer cortical surface (lh.pial / rh.pial)"
        )
        inputForm.addRow("Cortical Surface:", self.modelSelector)

        # ── 2-B  Interaction panel ────────────────────────────────────
        interBox = ctk.ctkCollapsibleButton()
        interBox.text = "Interactive Surface Picking"
        interBox.collapsed = False
        self.layout.addWidget(interBox)
        interForm = qt.QFormLayout(interBox)

        # Target slice view
        self.sliceViewCombo = qt.QComboBox()
        self.sliceViewCombo.addItems(["Red", "Yellow", "Green"])
        self.sliceViewCombo.setToolTip("Which 2-D view to reorient")
        interForm.addRow("Target Slice View:", self.sliceViewCombo)

        # Toggle button
        self.pickingButton = qt.QPushButton("Enable Surface Picking")
        self.pickingButton.setCheckable(True)
        self.pickingButton.setToolTip(
            "Activate picking mode, then click any point on the cortical surface "
            "in the 3-D view"
        )
        self.pickingButton.toggled.connect(self._onPickingToggled)
        interForm.addRow(self.pickingButton)

        # Status readouts
        self.pickedPointLabel = qt.QLabel("—")
        interForm.addRow("Picked Point (RAS):", self.pickedPointLabel)

        self.normalLabel = qt.QLabel("—")
        interForm.addRow("Surface Normal:", self.normalLabel)

        # ── 2-C  Resampling panel ─────────────────────────────────────
        resBox = ctk.ctkCollapsibleButton()
        resBox.text = "Generate Resampled Volume  (optional)"
        resBox.collapsed = True
        self.layout.addWidget(resBox)
        resForm = qt.QFormLayout(resBox)

        self.spacingSpinBox = qt.QDoubleSpinBox()
        self.spacingSpinBox.minimum    = 0.1
        self.spacingSpinBox.maximum    = 10.0
        self.spacingSpinBox.value      = 1.0
        self.spacingSpinBox.singleStep = 0.1
        self.spacingSpinBox.setToolTip("Out-of-plane slice spacing (mm)")
        resForm.addRow("Slice Spacing (mm):", self.spacingSpinBox)

        self.numSlicesSpinBox = qt.QSpinBox()
        self.numSlicesSpinBox.minimum = 1
        self.numSlicesSpinBox.maximum = 500
        self.numSlicesSpinBox.value   = 60
        self.numSlicesSpinBox.setToolTip("Total number of output slices")
        resForm.addRow("Number of Slices:", self.numSlicesSpinBox)

        self.outputNameEdit = qt.QLineEdit("NormalSlices")
        resForm.addRow("Output Volume Name:", self.outputNameEdit)

        self.resampleButton = qt.QPushButton("Generate Resampled Volume")
        self.resampleButton.clicked.connect(self._onGenerateResampled)
        resForm.addRow(self.resampleButton)

        # ── 2-D  Export hint ──────────────────────────────────────────
        exportBox = ctk.ctkCollapsibleButton()
        exportBox.text = "Export to DICOM  (optional)"
        exportBox.collapsed = True
        self.layout.addWidget(exportBox)
        exportForm = qt.QFormLayout(exportBox)
        hint = qt.QLabel(
            "After generating the resampled volume, use\n"
            "File → Export to DICOM  (or the DICOM module)\n"
            "to save the output as a DICOM series."
        )
        hint.setWordWrap(True)
        exportForm.addRow(hint)

        self.layout.addStretch(1)

    # ------------------------------------------------------------------
    def cleanup(self):
        self.removeObservers()
        if self.logic:
            self.logic.stopPicking()

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _onPickingToggled(self, checked):
        if checked:
            volumeNode = self.volumeSelector.currentNode()
            modelNode  = self.modelSelector.currentNode()
            if not volumeNode or not modelNode:
                slicer.util.errorDisplay(
                    "Please select both an MRI volume and a cortical surface model "
                    "before enabling surface picking."
                )
                self.pickingButton.setChecked(False)
                return
            sliceViewName = self.sliceViewCombo.currentText
            self.logic.startPicking(
                volumeNode    = volumeNode,
                modelNode     = modelNode,
                sliceViewName = sliceViewName,
                onPickCallback = self._onSurfacePicked,
            )
            self.pickingButton.setText("Disable Surface Picking  [active]")
            self.pickingButton.setStyleSheet(
                "background-color:#d4edda; color:#155724;"
            )
        else:
            self.logic.stopPicking()
            self.pickingButton.setText("Enable Surface Picking")
            self.pickingButton.setStyleSheet("")

    def _onSurfacePicked(self, ras_point, normal):
        self.pickedPointLabel.setText(
            "(%.2f,  %.2f,  %.2f)" % (ras_point[0], ras_point[1], ras_point[2])
        )
        self.normalLabel.setText(
            "(%.3f,  %.3f,  %.3f)" % (normal[0], normal[1], normal[2])
        )

    def _onGenerateResampled(self):
        if not self.logic.hasValidPick():
            slicer.util.errorDisplay(
                "No surface point has been picked yet.\n"
                "Please enable picking and click a point on the cortical surface first."
            )
            return
        volumeNode = self.volumeSelector.currentNode()
        if not volumeNode:
            slicer.util.errorDisplay("Please select an MRI volume.")
            return
        outputName = self.outputNameEdit.text.strip() or "NormalSlices"
        try:
            self.logic.generateResampledVolume(
                inputVolume      = volumeNode,
                sliceSpacing     = self.spacingSpinBox.value,
                numSlices        = self.numSlicesSpinBox.value,
                outputVolumeName = outputName,
            )
            slicer.util.infoDisplay(
                "Resampled volume '%s' created.\n"
                "Export via File → Export to DICOM." % outputName
            )
        except Exception as exc:
            slicer.util.errorDisplay("Resampling failed:\n%s" % str(exc))
            import traceback
            traceback.print_exc()


# =============================================================================
# 3. Logic — algorithms
# =============================================================================

class SurfaceNormalSlicerLogic(ScriptedLoadableModuleLogic):
    """
    Core algorithms:
      - Build a spatial index on the cortical surface.
      - Compute the outward surface normal at a picked point.
      - Reorient a 2-D slice view to the tangent plane.
      - Resample the MRI volume along the normal axis.
    """

    _SLICE_NODE_IDS = {
        "Red":    "vtkMRMLSliceNodeRed",
        "Yellow": "vtkMRMLSliceNodeYellow",
        "Green":  "vtkMRMLSliceNodeGreen",
    }

    def __init__(self):
        ScriptedLoadableModuleLogic.__init__(self)
        self._modelNode      = None
        self._volumeNode     = None
        self._sliceViewName  = "Red"
        self._onPickCallback = None

        self._polydata       = None
        self._pointLocator   = None
        self._normalsArray   = None

        self._fiducialNode        = None
        self._fiducialObserverTag = None

        self._lastRAS    = None
        self._lastNormal = None

    # ------------------------------------------------------------------
    # Public — picking
    # ------------------------------------------------------------------

    def startPicking(self, volumeNode, modelNode, sliceViewName, onPickCallback):
        """
        Activate interactive surface picking.

        Places a single-point Fiducial node that snaps to the visible surface.
        Every time the point is moved, the slice view is reoriented and
        `onPickCallback(ras_point, normal)` is called.
        """
        self.stopPicking()

        self._volumeNode     = volumeNode
        self._modelNode      = modelNode
        self._sliceViewName  = sliceViewName
        self._onPickCallback = onPickCallback

        self._buildSurfaceIndex(modelNode)

        # Create a temporary fiducial node
        self._fiducialNode = slicer.mrmlScene.AddNewNodeByClass(
            "vtkMRMLMarkupsFiducialNode", "_SNS_Pick"
        )
        dn = self._fiducialNode.GetDisplayNode()
        dn.SetTextScale(0)
        dn.SetGlyphScale(1.5)
        dn.SetSelectedColor(1.0, 0.5, 0.0)
        # Snap to the visible surface in the 3-D view
        dn.SetSnapMode(
            slicer.vtkMRMLMarkupsDisplayNode.SnapModeToVisibleSurface
        )
        self._fiducialNode.SetMaximumNumberOfControlPoints(1)

        self._fiducialObserverTag = self._fiducialNode.AddObserver(
            slicer.vtkMRMLMarkupsNode.PointModifiedEvent,
            self._onFiducialMoved,
        )

        # Switch to "place" interaction mode
        interactionNode = slicer.app.applicationLogic().GetInteractionNode()
        selectionNode   = slicer.app.applicationLogic().GetSelectionNode()
        selectionNode.SetReferenceActivePlaceNodeClassName(
            "vtkMRMLMarkupsFiducialNode"
        )
        selectionNode.SetActivePlaceNodeID(self._fiducialNode.GetID())
        interactionNode.SetCurrentInteractionMode(
            slicer.vtkMRMLInteractionNode.Place
        )
        print("[SurfaceNormalSlicer] Picking ON — click the cortical surface.")

    def stopPicking(self):
        """Deactivate picking and remove temporary nodes."""
        try:
            interactionNode = slicer.app.applicationLogic().GetInteractionNode()
            interactionNode.SetCurrentInteractionMode(
                slicer.vtkMRMLInteractionNode.ViewTransform
            )
        except Exception:
            pass

        if self._fiducialNode and self._fiducialObserverTag is not None:
            self._fiducialNode.RemoveObserver(self._fiducialObserverTag)
            self._fiducialObserverTag = None

        if self._fiducialNode:
            slicer.mrmlScene.RemoveNode(self._fiducialNode)
            self._fiducialNode = None

        print("[SurfaceNormalSlicer] Picking OFF.")

    def hasValidPick(self):
        return (self._lastRAS is not None) and (self._lastNormal is not None)

    # ------------------------------------------------------------------
    # Public — resampling
    # ------------------------------------------------------------------

    def generateResampledVolume(
        self, inputVolume, sliceSpacing, numSlices, outputVolumeName
    ):
        """
        Resample the MRI volume along the current surface normal axis.

        The output stack is centred on the last picked point and spans
        `numSlices * sliceSpacing` mm along the normal.
        """
        if not self.hasValidPick():
            raise RuntimeError(
                "No surface point picked. Pick a point on the cortical surface first."
            )

        center = self._lastRAS
        normal = self._lastNormal
        xDir, yDir = self._orthogonalBasis(normal)

        # Preserve in-plane extent of the input volume
        inputImageData = inputVolume.GetImageData()
        inputSpacing   = inputVolume.GetSpacing()
        inputExtent    = inputImageData.GetExtent()
        outW = inputExtent[1] - inputExtent[0] + 1
        outH = inputExtent[3] - inputExtent[2] + 1

        halfDepth = (numSlices * sliceSpacing) / 2.0
        origin    = center - normal * halfDepth

        outputExtent = [0, outW - 1, 0, outH - 1, 0, numSlices - 1]

        resliceAxes = self._buildResliceMatrix(origin, xDir, yDir, normal)

        reslice = vtk.vtkImageReslice()
        reslice.SetInputData(inputImageData)
        reslice.SetResliceAxes(resliceAxes)
        reslice.SetOutputSpacing(inputSpacing[0], inputSpacing[1], sliceSpacing)
        reslice.SetOutputExtent(outputExtent)
        reslice.SetInterpolationModeToLinear()
        reslice.SetBackgroundLevel(0)
        reslice.Update()

        outputVolume = slicer.mrmlScene.AddNewNodeByClass(
            "vtkMRMLScalarVolumeNode", outputVolumeName
        )
        outputVolume.SetAndObserveImageData(reslice.GetOutput())

        ijkToRas = vtk.vtkMatrix4x4()
        ijkToRas.DeepCopy(resliceAxes)
        ijkToRas.Invert()
        outputVolume.SetIJKToRASMatrix(ijkToRas)

        inputDisplayNode = inputVolume.GetDisplayNode()
        if inputDisplayNode:
            outputVolume.CreateDefaultDisplayNodes()
            outDisplay = outputVolume.GetDisplayNode()
            if outDisplay:
                outDisplay.SetAndObserveColorNodeID(
                    inputDisplayNode.GetColorNodeID()
                )
                outDisplay.SetWindow(inputDisplayNode.GetWindow())
                outDisplay.SetLevel(inputDisplayNode.GetLevel())

        slicer.util.setSliceViewerLayers(background=outputVolume)
        print(
            "[SurfaceNormalSlicer] Resampled volume '%s': %d slices × %.1f mm."
            % (outputVolumeName, numSlices, sliceSpacing)
        )
        return outputVolume

    # ------------------------------------------------------------------
    # Private — surface index
    # ------------------------------------------------------------------

    def _buildSurfaceIndex(self, modelNode):
        polydata = modelNode.GetPolyData()

        existingNormals = polydata.GetPointData().GetNormals()
        if existingNormals is None or existingNormals.GetNumberOfTuples() == 0:
            print("[SurfaceNormalSlicer] Computing surface normals …")
            nf = vtk.vtkPolyDataNormals()
            nf.SetInputData(polydata)
            nf.ComputePointNormalsOn()
            nf.ComputeCellNormalsOff()
            nf.SplittingOff()
            nf.ConsistencyOn()
            nf.AutoOrientNormalsOn()
            nf.Update()
            self._polydata = nf.GetOutput()
        else:
            self._polydata = polydata

        self._normalsArray = self._polydata.GetPointData().GetNormals()

        self._pointLocator = vtk.vtkPointLocator()
        self._pointLocator.SetDataSet(self._polydata)
        self._pointLocator.BuildLocator()

        print(
            "[SurfaceNormalSlicer] Index built: %d vertices."
            % self._polydata.GetNumberOfPoints()
        )

    # ------------------------------------------------------------------
    # Private — fiducial callback
    # ------------------------------------------------------------------

    def _onFiducialMoved(self, caller, event):
        if caller.GetNumberOfControlPoints() == 0:
            return

        ras = [0.0, 0.0, 0.0]
        caller.GetNthControlPointPositionWorld(0, ras)
        ras = np.array(ras)

        closestId  = self._pointLocator.FindClosestPoint(ras)
        closestRAS = np.array(self._polydata.GetPoint(closestId))
        normal     = np.array(self._normalsArray.GetTuple(closestId))
        norm_len   = np.linalg.norm(normal)
        if norm_len > 1e-12:
            normal = normal / norm_len

        self._lastRAS    = closestRAS
        self._lastNormal = normal

        self._updateSliceView(closestRAS, normal)

        if self._onPickCallback:
            self._onPickCallback(closestRAS, normal)

        print(
            "[SurfaceNormalSlicer] RAS=(%.2f, %.2f, %.2f)  "
            "N=(%.3f, %.3f, %.3f)"
            % (closestRAS[0], closestRAS[1], closestRAS[2],
               normal[0],     normal[1],     normal[2])
        )

    # ------------------------------------------------------------------
    # Private — slice view orientation
    # ------------------------------------------------------------------

    def _updateSliceView(self, centerRAS, normal):
        nodeId    = self._SLICE_NODE_IDS.get(
            self._sliceViewName, "vtkMRMLSliceNodeRed"
        )
        sliceNode = slicer.mrmlScene.GetNodeByID(nodeId)
        if not sliceNode:
            print(
                "[SurfaceNormalSlicer] WARNING: slice node '%s' not found." % nodeId
            )
            return

        xDir, yDir = self._orthogonalBasis(normal)

        # N = slice normal, T = in-plane transverse, P = centre point
        sliceNode.SetSliceToRASByNTP(
            normal[0],    normal[1],    normal[2],
            xDir[0],      xDir[1],      xDir[2],
            centerRAS[0], centerRAS[1], centerRAS[2],
            0,
        )
        sliceNode.UpdateMatrices()

    # ------------------------------------------------------------------
    # Private — geometry helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _orthogonalBasis(normal):
        """
        Return two unit vectors (xDir, yDir) spanning the plane perpendicular
        to `normal`, computed via Gram-Schmidt orthogonalisation.
        """
        if abs(normal[0]) < 0.9:
            ref = np.array([1.0, 0.0, 0.0])
        else:
            ref = np.array([0.0, 1.0, 0.0])

        xDir = ref - np.dot(ref, normal) * normal
        xLen = np.linalg.norm(xDir)
        if xLen > 1e-12:
            xDir /= xLen

        yDir = np.cross(normal, xDir)
        yLen = np.linalg.norm(yDir)
        if yLen > 1e-12:
            yDir /= yLen

        return xDir, yDir

    @staticmethod
    def _buildResliceMatrix(origin, xDir, yDir, zDir):
        """
        Build a 4×4 VTK matrix for vtkImageReslice.
        Columns encode the X, Y, Z axis directions and the origin.
        """
        m = vtk.vtkMatrix4x4()
        m.Identity()
        for row in range(3):
            m.SetElement(row, 0, xDir[row])
            m.SetElement(row, 1, yDir[row])
            m.SetElement(row, 2, zDir[row])
            m.SetElement(row, 3, origin[row])
        return m


# =============================================================================
# 4. Tests
# =============================================================================

class SurfaceNormalSlicerTest(ScriptedLoadableModuleTest):
    """Unit tests — run via Edit → Run Tests or the Reload&Test button."""

    def setUp(self):
        slicer.mrmlScene.Clear()

    def runTest(self):
        self.setUp()
        self.test_orthogonalBasis()
        self.test_resliceMatrix()
        self.test_normalComputation()
        self.test_fullResamplePipeline()

    # ------------------------------------------------------------------

    def test_orthogonalBasis(self):
        self.delayDisplay("Testing _orthogonalBasis …")
        logic = SurfaceNormalSlicerLogic()
        normals = [
            np.array([0.0, 0.0, 1.0]),
            np.array([1.0, 0.0, 0.0]),
            np.array([0.0, 1.0, 0.0]),
            np.array([1.0, 1.0, 1.0]) / math.sqrt(3),
        ]
        for n in normals:
            x, y = logic._orthogonalBasis(n)
            self.assertAlmostEqual(np.linalg.norm(x), 1.0, places=6)
            self.assertAlmostEqual(np.linalg.norm(y), 1.0, places=6)
            self.assertAlmostEqual(float(np.dot(x, y)),   0.0, places=6)
            self.assertAlmostEqual(float(np.dot(x, n)),   0.0, places=6)
            self.assertAlmostEqual(float(np.dot(y, n)),   0.0, places=6)
        self.delayDisplay("test_orthogonalBasis PASSED")

    # ------------------------------------------------------------------

    def test_resliceMatrix(self):
        self.delayDisplay("Testing _buildResliceMatrix …")
        logic  = SurfaceNormalSlicerLogic()
        origin = np.array([5.0, -10.0, 20.0])
        xDir   = np.array([1.0,   0.0,  0.0])
        yDir   = np.array([0.0,   1.0,  0.0])
        zDir   = np.array([0.0,   0.0,  1.0])
        m = logic._buildResliceMatrix(origin, xDir, yDir, zDir)
        self.assertAlmostEqual(m.GetElement(0, 3),   5.0, places=6)
        self.assertAlmostEqual(m.GetElement(1, 3), -10.0, places=6)
        self.assertAlmostEqual(m.GetElement(2, 3),  20.0, places=6)
        self.assertAlmostEqual(m.GetElement(0, 0),   1.0, places=6)
        self.assertAlmostEqual(m.GetElement(1, 1),   1.0, places=6)
        self.assertAlmostEqual(m.GetElement(2, 2),   1.0, places=6)
        self.delayDisplay("test_resliceMatrix PASSED")

    # ------------------------------------------------------------------

    def test_normalComputation(self):
        self.delayDisplay("Testing normal computation on a sphere …")
        sphere = vtk.vtkSphereSource()
        sphere.SetRadius(50.0)
        sphere.SetPhiResolution(32)
        sphere.SetThetaResolution(32)
        sphere.Update()

        modelNode = slicer.mrmlScene.AddNewNodeByClass(
            "vtkMRMLModelNode", "TestSphere"
        )
        modelNode.SetAndObservePolyData(sphere.GetOutput())
        modelNode.CreateDefaultDisplayNodes()

        logic = SurfaceNormalSlicerLogic()
        logic._buildSurfaceIndex(modelNode)

        testPoint = [50.0, 0.0, 0.0]
        closestId = logic._pointLocator.FindClosestPoint(testPoint)
        normal    = np.array(logic._normalsArray.GetTuple(closestId))
        normal   /= np.linalg.norm(normal)
        self.assertGreater(normal[0], 0.9)
        self.delayDisplay("test_normalComputation PASSED")

    # ------------------------------------------------------------------

    def test_fullResamplePipeline(self):
        self.delayDisplay("Testing full resample pipeline …")

        imageData = vtk.vtkImageData()
        imageData.SetDimensions(64, 64, 64)
        imageData.SetSpacing(1.0, 1.0, 1.0)
        imageData.AllocateScalars(vtk.VTK_SHORT, 1)
        imageData.GetPointData().GetScalars().Fill(200)

        inputVolume = slicer.mrmlScene.AddNewNodeByClass(
            "vtkMRMLScalarVolumeNode", "TestVolume"
        )
        inputVolume.SetAndObserveImageData(imageData)
        inputVolume.CreateDefaultDisplayNodes()

        logic = SurfaceNormalSlicerLogic()
        logic._lastRAS    = np.array([32.0, 32.0, 32.0])
        logic._lastNormal = np.array([0.0,  0.0,  1.0])

        out  = logic.generateResampledVolume(
            inputVolume      = inputVolume,
            sliceSpacing     = 2.0,
            numSlices        = 20,
            outputVolumeName = "TestOutput",
        )
        self.assertIsNotNone(out)
        dims = out.GetImageData().GetDimensions()
        self.assertEqual(dims[2], 20)
        self.delayDisplay("test_fullResamplePipeline PASSED")
