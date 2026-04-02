#-----------------------------------------------------------------------------
# Module: SurfaceNormalSlicer
# Python-only scripted module — no C++ compilation required.
#-----------------------------------------------------------------------------
set(MODULE_NAME SurfaceNormalSlicer)

#-----------------------------------------------------------------------------
# Python scripts
#-----------------------------------------------------------------------------
set(MODULE_PYTHON_SCRIPTS
  ${MODULE_NAME}.py
  )

#-----------------------------------------------------------------------------
# Resources
#-----------------------------------------------------------------------------
set(MODULE_PYTHON_RESOURCES
  Resources/Icons/${MODULE_NAME}.png
  )

#-----------------------------------------------------------------------------
# Build
#-----------------------------------------------------------------------------
slicerMacroBuildScriptedModule(
  NAME ${MODULE_NAME}
  SCRIPTS ${MODULE_PYTHON_SCRIPTS}
  RESOURCES ${MODULE_PYTHON_RESOURCES}
  WITH_GENERIC_TESTS
  )

#-----------------------------------------------------------------------------
# Testing
#-----------------------------------------------------------------------------
if(BUILD_TESTING)
  # Register the unittest subclass in the main script as a ctest.
  slicer_add_python_unittest(SCRIPT ${MODULE_NAME}.py)
endif()
