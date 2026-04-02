# SlicerSurfaceNormalSlicer

**Author**: Lu Aohan (2023012411)  
**Category**: Neuroimaging  
**Slicer version**: 5.x+

---

## Overview

**SurfaceNormalSlicer** is a 3D Slicer extension that enables FreeSurfer-guided oblique MRI slice reconstruction. Click any point on a cortical surface (`lh.pial` / `rh.pial`) in the 3-D view; the selected 2-D slice view is instantly reoriented to the **tangent plane** at that point, allowing you to scroll through oblique slices along the surface normal axis.

---

## Workflow

```
FreeSurfer recon-all  →  lh.pial / rh.pial
        ↓  Import via SlicerFreeSurfer extension
   Model Node (cortical surface mesh)
        ↓  + Original MRI (DICOM / NIfTI) as Scalar Volume Node
        ↓  Open "Surface Normal Slicer" module
        ↓  Click "Enable Surface Picking"
        ↓  Click any point on the cortical surface in the 3-D view
   Surface normal computed (vtkPointLocator + vtkPolyDataNormals)
        ↓  SetSliceToRASByNTP() → instant slice view reorientation
   Red/Yellow/Green view = tangent plane (scroll to step through slices)
        ↓  (optional) "Generate Resampled Volume" → vtkImageReslice
   New Volume Node  →  File → Export to DICOM
```

---

## Installation

### Option A — Install from Extension Manager (after official indexing)

1. Open 3D Slicer.
2. Go to **View** → **Extension Manager**.
3. Search for `SurfaceNormalSlicer`.
4. Click **Install**, then restart Slicer.

### Option B — Manual installation (current, before official indexing)

1. Download `SurfaceNormalSlicer.py` from this repository.
2. In Slicer: **Edit** → **Application Settings** → **Modules** → **Additional module paths** → add the folder containing `SurfaceNormalSlicer.py`.
3. Restart Slicer and search for `Surface Normal Slicer` in the module selector.

---

## Usage

1. Load your MRI volume (DICOM or NIfTI).
2. Load the FreeSurfer cortical surface via the **SlicerFreeSurfer** extension (drag-and-drop `lh.pial` or `rh.pial`), or convert it first with `mris_convert lh.pial lh.vtk`.
3. Open the **Surface Normal Slicer** module.
4. Select the MRI volume and the cortical surface model in the **Input** panel.
5. Click **Enable Surface Picking** and click any point on the cortical surface in the 3-D view.
6. The target slice view (Red by default) is immediately reoriented. Scroll to step through parallel oblique slices.
7. *(Optional)* Expand **Generate Resampled Volume**, set spacing and slice count, then click the button to create a new volume node.
8. *(Optional)* Export via **File → Export to DICOM**.

---

## License

MIT
