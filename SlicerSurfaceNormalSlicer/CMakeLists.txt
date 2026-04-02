cmake_minimum_required(VERSION 3.16.3...3.19.7 FATAL_ERROR)

project(SlicerSurfaceNormalSlicer)

#-----------------------------------------------------------------------------
# Extension meta-information
#-----------------------------------------------------------------------------
set(EXTENSION_HOMEPAGE
  "https://github.com/xuanyuelingwu/BioInformatics/tree/main/SlicerSurfaceNormalSlicer"
)
set(EXTENSION_CATEGORY "Neuroimaging")
set(EXTENSION_CONTRIBUTORS "Lu Aohan (2023012411)")
set(EXTENSION_DESCRIPTION
  "FreeSurfer-guided oblique MRI slice reconstruction. \
Click any point on a cortical surface (lh.pial / rh.pial) in the 3-D view; \
the selected 2-D slice view is instantly reoriented to the tangent plane at \
that point so you can scroll through oblique slices along the surface normal axis."
)
set(EXTENSION_ICONURL
  "https://raw.githubusercontent.com/xuanyuelingwu/BioInformatics/main/SlicerSurfaceNormalSlicer/SurfaceNormalSlicer/Resources/Icons/SurfaceNormalSlicer.png"
)
set(EXTENSION_SCREENSHOTURLS "")
set(EXTENSION_DEPENDS "NA")  # no other Slicer extensions required

#-----------------------------------------------------------------------------
# Extension dependencies
#-----------------------------------------------------------------------------
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
#-----------------------------------------------------------------------------
add_subdirectory(SurfaceNormalSlicer)
## NEXT_MODULE

#-----------------------------------------------------------------------------
# End
#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_CPACK})
