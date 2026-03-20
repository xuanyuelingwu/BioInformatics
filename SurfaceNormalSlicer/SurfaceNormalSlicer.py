#!/usr/bin/env python3
"""
SurfaceNormalSlicer: A 3D Slicer Python scripted module for FreeSurfer-guided
oblique MRI slice reconstruction.

Complete workflow:
  1. Load FreeSurfer cortical surface reconstruction (lh.pial / rh.pial) as a
     Model node in 3D Slicer.
  2. Load the original MRI volume (DICOM or NIfTI).
  3. Click any point on the cortical surface in the 3D view.
  4. The module computes the surface normal at that point (tangent plane normal).
  5. The Red slice view is instantly reoriented so that it is perpendicular to
     that normal — i.e., the slice plane IS the tangent plane at the clicked point.
  6. Scrolling the Red view steps through parallel slices along the normal axis.
  7. Optionally, generate a full resampled volume along the normal axis and
     export it as DICOM.

Author: 鲁奥晗
Student ID: 2023012411
License: MIT
"""

import math
import numpy as np
from typing import Optional, Tuple

import vtk
import slicer
import qt
import ctk
from slicer.ScriptedLoadableModule import (
    ScriptedLoadableModule,
    ScriptedLoadableModuleWidget,
    ScriptedLoadableModuleLogic,
    ScriptedLoadableModuleTest,
)
from slicer.util import VTKObservationMixin


# =============================================================================
# Module Class — metadata & registration
# =============================================================================

class SurfaceNormalSlicer(ScriptedLoadableModule):
    """
    Module metadata for SurfaceNormalSlicer.
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "Surface Normal Slicer"
        self.parent.categories = ["Neuroimaging"]
        self.parent.dependencies = []
        self.parent.contributors = ["鲁奥晗 (2023012411)"]
        self.parent.helpText = """
        <h3>Surface Normal Slicer</h3>
        <p>This module enables FreeSurfer-guided oblique MRI slice reconstruction
        directly inside 3D Slicer.</p>
        <p><b>Typical workflow:</b></p>
        <ol>
          <li>Import the FreeSurfer cortical surface (e.g. <tt>lh.pial</tt> or
              <tt>rh.pial</tt>) as a Model node via the
              <i>SlicerFreeSurfer</i> extension or by converting to VTK/OBJ format.</li>
          <li>Load the original MRI volume (DICOM or NIfTI).</li>
          <li>Select both nodes in the <b>Input</b> panel.</li>
          <li>Click <b>Enable Surface Picking</b> and then click any point on the
              cortical surface in the 3D view.</li>
          <li>The Red slice view is immediately reoriented to the tangent plane at
              that point. Scroll to step through parallel slices.</li>
          <li>Optionally click <b>Generate Resampled Volume</b> to bake the series
              into a new Volume node (which can then be exported as DICOM).</li>
        </ol>
        """
        self.parent.acknowledgementText = (
            "Developed with 3D Slicer, VTK, and Python. "
            "FreeSurfer surface import supported via the SlicerFreeSurfer extension."
        )


# =============================================================================
# Widget Class — user interface
# =============================================================================

class SurfaceNormalSlicerWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
    """
    UI class for SurfaceNormalSlicer.
    """

    def __init__(self, parent=None):
        ScriptedLoadableModuleWidget.__init__(self, parent)
        VTKObservationMixin.__init__(self)
        self.logic: Optional[SurfaceNormalSlicerLogic] = None
        self._pickingEnabled = False

    # ------------------------------------------------------------------
    # setup
    # ------------------------------------------------------------------

    def setup(self):
        ScriptedLoadableModuleWidget.setup(self)
        self.logic = SurfaceNormalSlicerLogic()

        # ── Input ──────────────────────────────────────────────────────
        inputBox = ctk.ctkCollapsibleButton()
        inputBox.text = "Input"
        self.layout.addWidget(inputBox)
        inputForm = qt.QFormLayout(inputBox)

        # MRI volume selector
        self.volumeSelector = slicer.qMRMLNodeComboBox()
        self.volumeSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
        self.volumeSelector.selectNodeUponCreation = True
        self.volumeSelector.addEnabled = False
        self.volumeSelector.removeEnabled = False
        self.volumeSelector.noneEnabled = False
        self.volumeSelector.showHidden = False
        self.volumeSelector.setMRMLScene(slicer.mrmlScene)
        self.volumeSelector.setToolTip("Select the MRI volume (DICOM or NIfTI)")
        inputForm.addRow("MRI Volume:", self.volumeSelector)

        # Surface model selector
        self.modelSelector = slicer.qMRMLNodeComboBox()
        self.modelSelector.nodeTypes = ["vtkMRMLModelNode"]
        self.modelSelector.selectNodeUponCreation = False
        self.modelSelector.addEnabled = False
        self.modelSelector.removeEnabled = False
        self.modelSelector.noneEnabled = False
        self.modelSelector.showHidden = False
        self.modelSelector.setMRMLScene(slicer.mrmlScene)
        self.modelSelector.setToolTip(
            "Select the FreeSurfer cortical surface model (lh.pial / rh.pial)"
        )
        inputForm.addRow("Cortical Surface:", self.modelSelector)

        # ── Interaction ────────────────────────────────────────────────
        interactionBox = ctk.ctkCollapsibleButton()
        interactionBox.text = "Interactive Surface Picking"
        interactionBox.collapsed = False
        self.layout.addWidget(interactionBox)
        interactionForm = qt.QFormLayout(interactionBox)

        # Enable/disable picking toggle
        self.pickingButton = qt.QPushButton("Enable Surface Picking")
        self.pickingButton.setCheckable(True)
        self.pickingButton.setToolTip(
            "Click to activate picking mode, then click any point on the "
            "cortical surface in the 3D view"
        )
        self.pickingButton.toggled.connect(self._onPickingToggled)
        interactionForm.addRow(self.pickingButton)

        # Status labels
        self.pickedPointLabel = qt.QLabel("—")
        self.pickedPointLabel.setToolTip("RAS coordinates of the last picked point")
        interactionForm.addRow("Picked Point (RAS):", self.pickedPointLabel)

        self.normalLabel = qt.QLabel("—")
        self.normalLabel.setToolTip("Surface normal at the picked point")
        interactionForm.addRow("Surface Normal:", self.normalLabel)

        # Slice view selector
        self.sliceViewCombo = qt.QComboBox()
        self.sliceViewCombo.addItems(["Red", "Yellow", "Green"])
        self.sliceViewCombo.setToolTip(
            "Which 2D slice view to reorient to the tangent plane"
        )
        interactionForm.addRow("Target Slice View:", self.sliceViewCombo)

        # ── Resampling ─────────────────────────────────────────────────
        resampleBox = ctk.ctkCollapsibleButton()
        resampleBox.text = "Generate Resampled Volume (Optional)"
        resampleBox.collapsed = True
        self.layout.addWidget(resampleBox)
        resampleForm = qt.QFormLayout(resampleBox)

        self.spacingSpinBox = qt.QDoubleSpinBox()
        self.spacingSpinBox.minimum = 0.1
        self.spacingSpinBox.maximum = 10.0
        self.spacingSpinBox.value = 1.0
        self.spacingSpinBox.singleStep = 0.1
        self.spacingSpinBox.setToolTip("Slice spacing for the resampled volume (mm)")
        resampleForm.addRow("Slice Spacing (mm):", self.spacingSpinBox)

        self.numSlicesSpinBox = qt.QSpinBox()
        self.numSlicesSpinBox.minimum = 1
        self.numSlicesSpinBox.maximum = 500
        self.numSlicesSpinBox.value = 60
        self.numSlicesSpinBox.setToolTip("Number of slices to generate")
        resampleForm.addRow("Number of Slices:", self.numSlicesSpinBox)

        self.outputNameEdit = qt.QLineEdit("NormalSlices")
        self.outputNameEdit.setToolTip("Name for the output resampled volume node")
        resampleForm.addRow("Output Volume Name:", self.outputNameEdit)

        self.resampleButton = qt.QPushButton("Generate Resampled Volume")
        self.resampleButton.setToolTip(
            "Resample the MRI volume along the current surface normal axis "
            "and create a new Volume node"
        )
        self.resampleButton.clicked.connect(self._onGenerateResampled)
        resampleForm.addRow(self.resampleButton)

        # ── DICOM export hint ──────────────────────────────────────────
        exportBox = ctk.ctkCollapsibleButton()
        exportBox.text = "Export to DICOM (Optional)"
        exportBox.collapsed = True
        self.layout.addWidget(exportBox)
        exportForm = qt.QFormLayout(exportBox)

        exportHint = qt.QLabel(
            "After generating the resampled volume, use\n"
            "File → Export to DICOM  (or the DICOM module)\n"
            "to save the output volume as a DICOM series."
        )
        exportHint.setWordWrap(True)
        exportForm.addRow(exportHint)

        self.layout.addStretch(1)

    # ------------------------------------------------------------------
    # cleanup
    # ------------------------------------------------------------------

    def cleanup(self):
        self.removeObservers()
        if self.logic:
            self.logic.stopPicking()

    # ------------------------------------------------------------------
    # slots
    # ------------------------------------------------------------------

    def _onPickingToggled(self, checked: bool):
        """Activate or deactivate interactive surface picking."""
        self._pickingEnabled = checked

        if checked:
            # Validate inputs first
            volumeNode = self.volumeSelector.currentNode()
            modelNode = self.modelSelector.currentNode()
            if not volumeNode or not modelNode:
                slicer.util.errorDisplay(
                    "Please select both an MRI volume and a cortical surface model "
                    "before enabling surface picking."
                )
                self.pickingButton.setChecked(False)
                return

            sliceViewName = self.sliceViewCombo.currentText
            self.logic.startPicking(
                volumeNode=volumeNode,
                modelNode=modelNode,
                sliceViewName=sliceViewName,
                onPickCallback=self._onSurfacePicked,
            )
            self.pickingButton.setText("Disable Surface Picking  [active]")
            self.pickingButton.setStyleSheet("background-color: #d4edda; color: #155724;")
        else:
            self.logic.stopPicking()
            self.pickingButton.setText("Enable Surface Picking")
            self.pickingButton.setStyleSheet("")

    def _onSurfacePicked(self, ras_point: np.ndarray, normal: np.ndarray):
        """Called by logic whenever the user picks a new point on the surface."""
        self.pickedPointLabel.setText(
            f"({ras_point[0]:.2f},  {ras_point[1]:.2f},  {ras_point[2]:.2f})"
        )
        self.normalLabel.setText(
            f"({normal[0]:.3f},  {normal[1]:.3f},  {normal[2]:.3f})"
        )

    def _onGenerateResampled(self):
        """Generate a full resampled volume along the current normal axis."""
        if not self.logic.hasValidPick():
            slicer.util.errorDisplay(
                "No surface point has been picked yet. "
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
                inputVolume=volumeNode,
                sliceSpacing=self.spacingSpinBox.value,
                numSlices=self.numSlicesSpinBox.value,
                outputVolumeName=outputName,
            )
            slicer.util.infoDisplay(
                f"Resampled volume '{outputName}' created successfully.\n"
                "You can now export it via File → Export to DICOM."
            )
        except Exception as exc:
            slicer.util.errorDisplay(f"Resampling failed:\n{exc}")
            import traceback
            traceback.print_exc()


# =============================================================================
# Logic Class — core algorithms
# =============================================================================

class SurfaceNormalSlicerLogic(ScriptedLoadableModuleLogic):
    """
    Core logic for SurfaceNormalSlicer.

    Responsibilities:
      - Manage interactive surface picking via a Markups Fiducial node.
      - Compute the surface normal at the picked point.
      - Reorient a 2D slice view to the tangent plane at that point.
      - Optionally resample the MRI volume along the normal axis.
    """

    # Slicer colour names → MRML node IDs
    _SLICE_NODE_IDS = {
        "Red":    "vtkMRMLSliceNodeRed",
        "Yellow": "vtkMRMLSliceNodeYellow",
        "Green":  "vtkMRMLSliceNodeGreen",
    }

    def __init__(self):
        ScriptedLoadableModuleLogic.__init__(self)

        # State
        self._modelNode = None
        self._volumeNode = None
        self._sliceViewName = "Red"
        self._onPickCallback = None

        # Cached geometry
        self._polydata: Optional[vtk.vtkPolyData] = None
        self._pointLocator: Optional[vtk.vtkPointLocator] = None
        self._normalsArray: Optional[vtk.vtkFloatArray] = None

        # The fiducial node used for interactive picking
        self._fiducialNode: Optional[slicer.vtkMRMLMarkupsFiducialNode] = None
        self._fiducialObserverTag: Optional[int] = None

        # Last valid pick
        self._lastRAS: Optional[np.ndarray] = None
        self._lastNormal: Optional[np.ndarray] = None

    # ------------------------------------------------------------------
    # Public API — picking
    # ------------------------------------------------------------------

    def startPicking(
        self,
        volumeNode,
        modelNode,
        sliceViewName: str,
        onPickCallback,
    ):
        """
        Activate interactive surface picking.

        Creates (or reuses) a single-point Fiducial node that the user can
        place/drag on the cortical surface in the 3D view.  Every time the
        point moves, the slice view is reoriented and `onPickCallback` is
        called with (ras_point, normal).

        Args:
            volumeNode: The MRI volume node.
            modelNode:  The FreeSurfer cortical surface model node.
            sliceViewName: "Red", "Yellow", or "Green".
            onPickCallback: Callable(ras_point: np.ndarray, normal: np.ndarray).
        """
        self.stopPicking()  # clean up any previous session

        self._volumeNode = volumeNode
        self._modelNode = modelNode
        self._sliceViewName = sliceViewName
        self._onPickCallback = onPickCallback

        # Pre-compute normals and build spatial index
        self._buildSurfaceIndex(modelNode)

        # Create a dedicated fiducial node for picking
        self._fiducialNode = slicer.mrmlScene.AddNewNodeByClass(
            "vtkMRMLMarkupsFiducialNode", "_SurfaceNormalSlicer_Pick"
        )
        self._fiducialNode.GetDisplayNode().SetTextScale(0)          # hide label
        self._fiducialNode.GetDisplayNode().SetGlyphScale(1.5)
        self._fiducialNode.GetDisplayNode().SetSelectedColor(1, 0.5, 0)  # orange
        self._fiducialNode.GetDisplayNode().SetSnapMode(
            slicer.vtkMRMLMarkupsDisplayNode.SnapModeToVisibleSurface
        )
        self._fiducialNode.SetMaximumNumberOfControlPoints(1)

        # Observe point placement / movement
        self._fiducialObserverTag = self._fiducialNode.AddObserver(
            slicer.vtkMRMLMarkupsNode.PointModifiedEvent,
            self._onFiducialMoved,
        )

        # Switch Slicer to "place fiducial" interaction mode
        interactionNode = slicer.app.applicationLogic().GetInteractionNode()
        selectionNode = slicer.app.applicationLogic().GetSelectionNode()
        selectionNode.SetReferenceActivePlaceNodeClassName(
            "vtkMRMLMarkupsFiducialNode"
        )
        selectionNode.SetActivePlaceNodeID(self._fiducialNode.GetID())
        interactionNode.SetCurrentInteractionMode(
            slicer.vtkMRMLInteractionNode.Place
        )

        print("[SurfaceNormalSlicer] Picking activated. Click on the cortical surface.")

    def stopPicking(self):
        """Deactivate picking and clean up resources."""
        # Restore normal interaction mode
        try:
            interactionNode = slicer.app.applicationLogic().GetInteractionNode()
            interactionNode.SetCurrentInteractionMode(
                slicer.vtkMRMLInteractionNode.ViewTransform
            )
        except Exception:
            pass

        # Remove observer
        if self._fiducialNode and self._fiducialObserverTag is not None:
            self._fiducialNode.RemoveObserver(self._fiducialObserverTag)
            self._fiducialObserverTag = None

        # Remove the temporary fiducial node from the scene
        if self._fiducialNode:
            slicer.mrmlScene.RemoveNode(self._fiducialNode)
            self._fiducialNode = None

        print("[SurfaceNormalSlicer] Picking deactivated.")

    def hasValidPick(self) -> bool:
        """Return True if a valid surface point has been picked."""
        return self._lastRAS is not None and self._lastNormal is not None

    # ------------------------------------------------------------------
    # Public API — resampling
    # ------------------------------------------------------------------

    def generateResampledVolume(
        self,
        inputVolume,
        sliceSpacing: float,
        numSlices: int,
        outputVolumeName: str,
    ):
        """
        Resample the MRI volume along the current surface normal axis.

        The output volume is centred on the last picked point and extends
        `numSlices * sliceSpacing / 2` mm in each direction along the normal.

        Args:
            inputVolume:       Source MRI volume node.
            sliceSpacing:      Distance between output slices (mm).
            numSlices:         Total number of output slices.
            outputVolumeName:  Name for the new volume node.

        Returns:
            The newly created vtkMRMLScalarVolumeNode.
        """
        if not self.hasValidPick():
            raise RuntimeError(
                "No surface point has been picked. "
                "Please pick a point on the cortical surface first."
            )

        center = self._lastRAS
        normal = self._lastNormal

        # Compute orthogonal basis
        xDir, yDir = self._orthogonalBasis(normal)

        # Determine output extent (preserve in-plane resolution of input)
        inputImageData = inputVolume.GetImageData()
        inputSpacing = np.array(inputVolume.GetSpacing())
        inputExtent = inputImageData.GetExtent()
        outWidth = inputExtent[1] - inputExtent[0] + 1
        outHeight = inputExtent[3] - inputExtent[2] + 1

        # Centre the stack on the picked point
        halfDepth = (numSlices * sliceSpacing) / 2.0
        origin = center - normal * halfDepth

        outputExtent = [0, outWidth - 1, 0, outHeight - 1, 0, numSlices - 1]

        # Build reslice matrix
        resliceAxes = self._buildResliceMatrix(origin, xDir, yDir, normal)

        # Reslice
        reslice = vtk.vtkImageReslice()
        reslice.SetInputData(inputImageData)
        reslice.SetResliceAxes(resliceAxes)
        reslice.SetOutputSpacing(inputSpacing[0], inputSpacing[1], sliceSpacing)
        reslice.SetOutputExtent(outputExtent)
        reslice.SetInterpolationModeToLinear()
        reslice.SetBackgroundLevel(0)
        reslice.Update()

        outputImageData = reslice.GetOutput()

        # Create MRML node
        outputVolume = slicer.mrmlScene.AddNewNodeByClass(
            "vtkMRMLScalarVolumeNode", outputVolumeName
        )
        outputVolume.SetAndObserveImageData(outputImageData)

        ijkToRas = vtk.vtkMatrix4x4()
        ijkToRas.DeepCopy(resliceAxes)
        ijkToRas.Invert()
        outputVolume.SetIJKToRASMatrix(ijkToRas)

        # Copy display settings
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
            f"[SurfaceNormalSlicer] Resampled volume '{outputVolumeName}' created: "
            f"{numSlices} slices × {sliceSpacing} mm."
        )
        return outputVolume

    # ------------------------------------------------------------------
    # Private — surface index
    # ------------------------------------------------------------------

    def _buildSurfaceIndex(self, modelNode):
        """
        Pre-compute point normals and build a vtkPointLocator for fast
        nearest-neighbour queries on the cortical surface.
        """
        polydata = modelNode.GetPolyData()

        # Generate normals if not already present
        existingNormals = polydata.GetPointData().GetNormals()
        if existingNormals is None or existingNormals.GetNumberOfTuples() == 0:
            print("[SurfaceNormalSlicer] Computing surface normals...")
            normalsFilter = vtk.vtkPolyDataNormals()
            normalsFilter.SetInputData(polydata)
            normalsFilter.ComputePointNormalsOn()
            normalsFilter.ComputeCellNormalsOff()
            normalsFilter.SplittingOff()        # preserve topology
            normalsFilter.ConsistencyOn()
            normalsFilter.AutoOrientNormalsOn()  # ensure outward-facing normals
            normalsFilter.Update()
            self._polydata = normalsFilter.GetOutput()
        else:
            self._polydata = polydata

        self._normalsArray = self._polydata.GetPointData().GetNormals()

        # Build spatial index
        self._pointLocator = vtk.vtkPointLocator()
        self._pointLocator.SetDataSet(self._polydata)
        self._pointLocator.BuildLocator()

        print(
            f"[SurfaceNormalSlicer] Surface index built: "
            f"{self._polydata.GetNumberOfPoints()} vertices."
        )

    # ------------------------------------------------------------------
    # Private — fiducial callback
    # ------------------------------------------------------------------

    def _onFiducialMoved(self, caller, event):
        """
        Called whenever the user places or moves the picking fiducial.
        Computes the surface normal at the new position and updates the
        slice view orientation.
        """
        if caller.GetNumberOfControlPoints() == 0:
            return

        # Get the current fiducial position in RAS
        ras = np.zeros(3)
        caller.GetNthControlPointPositionWorld(0, ras)

        # Find closest point on the cortical surface
        closestId = self._pointLocator.FindClosestPoint(ras)
        closestRAS = np.array(self._polydata.GetPoint(closestId))
        normal = np.array(self._normalsArray.GetTuple(closestId))
        normal = normal / (np.linalg.norm(normal) + 1e-12)

        # Cache
        self._lastRAS = closestRAS
        self._lastNormal = normal

        # Update the slice view
        self._updateSliceView(closestRAS, normal)

        # Notify the UI
        if self._onPickCallback:
            self._onPickCallback(closestRAS, normal)

        print(
            f"[SurfaceNormalSlicer] Picked RAS=({closestRAS[0]:.2f}, "
            f"{closestRAS[1]:.2f}, {closestRAS[2]:.2f})  "
            f"Normal=({normal[0]:.3f}, {normal[1]:.3f}, {normal[2]:.3f})"
        )

    # ------------------------------------------------------------------
    # Private — slice view orientation
    # ------------------------------------------------------------------

    def _updateSliceView(self, centerRAS: np.ndarray, normal: np.ndarray):
        """
        Reorient the target 2D slice view so that its plane is the tangent
        plane at the picked point (i.e., the slice plane normal == surface normal).

        Args:
            centerRAS: The picked point in RAS coordinates.
            normal:    The outward surface normal at that point (unit vector).
        """
        nodeId = self._SLICE_NODE_IDS.get(self._sliceViewName, "vtkMRMLSliceNodeRed")
        sliceNode = slicer.mrmlScene.GetNodeByID(nodeId)
        if not sliceNode:
            print(f"[SurfaceNormalSlicer] WARNING: slice node '{nodeId}' not found.")
            return

        # Compute orthogonal in-plane axes
        xDir, yDir = self._orthogonalBasis(normal)

        # SetSliceToRASByNTP(nx,ny,nz, tx,ty,tz, px,py,pz, mode)
        #   N = slice normal (= our surface normal)
        #   T = in-plane "transverse" direction (= xDir)
        #   P = a point the slice passes through (= picked point)
        sliceNode.SetSliceToRASByNTP(
            normal[0], normal[1], normal[2],
            xDir[0],   xDir[1],   xDir[2],
            centerRAS[0], centerRAS[1], centerRAS[2],
            0,
        )
        sliceNode.UpdateMatrices()

    # ------------------------------------------------------------------
    # Private — geometry helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _orthogonalBasis(
        normal: np.ndarray,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute two orthogonal unit vectors spanning the plane perpendicular
        to `normal` using the Gram-Schmidt process.

        Returns:
            (xDir, yDir) — both unit vectors, mutually orthogonal and
            orthogonal to `normal`.
        """
        # Choose a reference vector not (nearly) parallel to normal
        if abs(normal[0]) < 0.9:
            ref = np.array([1.0, 0.0, 0.0])
        else:
            ref = np.array([0.0, 1.0, 0.0])

        xDir = ref - np.dot(ref, normal) * normal
        xDir /= np.linalg.norm(xDir)

        yDir = np.cross(normal, xDir)
        yDir /= np.linalg.norm(yDir)

        return xDir, yDir

    @staticmethod
    def _buildResliceMatrix(
        origin: np.ndarray,
        xDir: np.ndarray,
        yDir: np.ndarray,
        zDir: np.ndarray,
    ) -> vtk.vtkMatrix4x4:
        """
        Build a 4×4 VTK matrix for vtkImageReslice.

        Columns encode the X, Y, Z axis directions and the translation
        (origin) of the output volume in RAS world coordinates.
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
# Test Class
# =============================================================================

class SurfaceNormalSlicerTest(ScriptedLoadableModuleTest):
    """
    Unit tests for SurfaceNormalSlicer.
    Run via Edit → Run Tests or the "Reload and Test" button in the module panel.
    """

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

        for normal in [
            np.array([0.0, 0.0, 1.0]),
            np.array([1.0, 0.0, 0.0]),
            np.array([0.0, 1.0, 0.0]),
            np.array([1.0, 1.0, 1.0]) / math.sqrt(3),
        ]:
            xDir, yDir = logic._orthogonalBasis(normal)
            self.assertAlmostEqual(np.linalg.norm(xDir), 1.0, places=6)
            self.assertAlmostEqual(np.linalg.norm(yDir), 1.0, places=6)
            self.assertAlmostEqual(float(np.dot(xDir, yDir)),    0.0, places=6)
            self.assertAlmostEqual(float(np.dot(xDir, normal)),  0.0, places=6)
            self.assertAlmostEqual(float(np.dot(yDir, normal)),  0.0, places=6)

        self.delayDisplay("test_orthogonalBasis PASSED")

    # ------------------------------------------------------------------

    def test_resliceMatrix(self):
        self.delayDisplay("Testing _buildResliceMatrix …")
        logic = SurfaceNormalSlicerLogic()

        origin = np.array([5.0, -10.0, 20.0])
        xDir   = np.array([1.0,   0.0,  0.0])
        yDir   = np.array([0.0,   1.0,  0.0])
        zDir   = np.array([0.0,   0.0,  1.0])

        m = logic._buildResliceMatrix(origin, xDir, yDir, zDir)

        self.assertAlmostEqual(m.GetElement(0, 3),  5.0, places=6)
        self.assertAlmostEqual(m.GetElement(1, 3), -10.0, places=6)
        self.assertAlmostEqual(m.GetElement(2, 3),  20.0, places=6)
        self.assertAlmostEqual(m.GetElement(0, 0),   1.0, places=6)
        self.assertAlmostEqual(m.GetElement(1, 1),   1.0, places=6)
        self.assertAlmostEqual(m.GetElement(2, 2),   1.0, places=6)

        self.delayDisplay("test_resliceMatrix PASSED")

    # ------------------------------------------------------------------

    def test_normalComputation(self):
        """Test that surface normals are computed correctly for a sphere."""
        self.delayDisplay("Testing surface normal computation on a sphere …")

        # Create a unit sphere
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

        # For a sphere centred at origin, the normal at any surface point
        # should be (approximately) parallel to the position vector.
        testPoint = np.array([50.0, 0.0, 0.0])
        closestId = logic._pointLocator.FindClosestPoint(testPoint)
        normal = np.array(logic._normalsArray.GetTuple(closestId))
        normal /= np.linalg.norm(normal)

        # The normal should point roughly in the +X direction
        self.assertGreater(normal[0], 0.9)

        self.delayDisplay("test_normalComputation PASSED")

    # ------------------------------------------------------------------

    def test_fullResamplePipeline(self):
        """End-to-end test: pick a point → resample → check output dimensions."""
        self.delayDisplay("Testing full resample pipeline …")

        # Synthetic 64³ volume
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

        # Manually inject a known pick result
        logic = SurfaceNormalSlicerLogic()
        logic._lastRAS    = np.array([32.0, 32.0, 32.0])
        logic._lastNormal = np.array([0.0, 0.0, 1.0])

        outputVolume = logic.generateResampledVolume(
            inputVolume=inputVolume,
            sliceSpacing=2.0,
            numSlices=20,
            outputVolumeName="TestOutput",
        )

        self.assertIsNotNone(outputVolume)
        dims = outputVolume.GetImageData().GetDimensions()
        self.assertEqual(dims[2], 20)

        self.delayDisplay("test_fullResamplePipeline PASSED")
