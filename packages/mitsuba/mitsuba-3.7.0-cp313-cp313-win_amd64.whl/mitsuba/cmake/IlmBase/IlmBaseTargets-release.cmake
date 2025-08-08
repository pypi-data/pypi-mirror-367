#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "IlmBase::Half" for configuration "Release"
set_property(TARGET IlmBase::Half APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(IlmBase::Half PROPERTIES
  IMPORTED_IMPLIB_RELEASE "${_IMPORT_PREFIX}/mitsuba/Half-mitsuba.lib"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/mitsuba/Half-mitsuba.dll"
  )

list(APPEND _cmake_import_check_targets IlmBase::Half )
list(APPEND _cmake_import_check_files_for_IlmBase::Half "${_IMPORT_PREFIX}/mitsuba/Half-mitsuba.lib" "${_IMPORT_PREFIX}/mitsuba/Half-mitsuba.dll" )

# Import target "IlmBase::Iex" for configuration "Release"
set_property(TARGET IlmBase::Iex APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(IlmBase::Iex PROPERTIES
  IMPORTED_IMPLIB_RELEASE "${_IMPORT_PREFIX}/mitsuba/Iex-mitsuba.lib"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/mitsuba/Iex-mitsuba.dll"
  )

list(APPEND _cmake_import_check_targets IlmBase::Iex )
list(APPEND _cmake_import_check_files_for_IlmBase::Iex "${_IMPORT_PREFIX}/mitsuba/Iex-mitsuba.lib" "${_IMPORT_PREFIX}/mitsuba/Iex-mitsuba.dll" )

# Import target "IlmBase::IexMath" for configuration "Release"
set_property(TARGET IlmBase::IexMath APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(IlmBase::IexMath PROPERTIES
  IMPORTED_IMPLIB_RELEASE "${_IMPORT_PREFIX}/mitsuba/IexMath-mitsuba.lib"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/mitsuba/IexMath-mitsuba.dll"
  )

list(APPEND _cmake_import_check_targets IlmBase::IexMath )
list(APPEND _cmake_import_check_files_for_IlmBase::IexMath "${_IMPORT_PREFIX}/mitsuba/IexMath-mitsuba.lib" "${_IMPORT_PREFIX}/mitsuba/IexMath-mitsuba.dll" )

# Import target "IlmBase::Imath" for configuration "Release"
set_property(TARGET IlmBase::Imath APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(IlmBase::Imath PROPERTIES
  IMPORTED_IMPLIB_RELEASE "${_IMPORT_PREFIX}/mitsuba/Imath-mitsuba.lib"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/mitsuba/Imath-mitsuba.dll"
  )

list(APPEND _cmake_import_check_targets IlmBase::Imath )
list(APPEND _cmake_import_check_files_for_IlmBase::Imath "${_IMPORT_PREFIX}/mitsuba/Imath-mitsuba.lib" "${_IMPORT_PREFIX}/mitsuba/Imath-mitsuba.dll" )

# Import target "IlmBase::IlmThread" for configuration "Release"
set_property(TARGET IlmBase::IlmThread APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(IlmBase::IlmThread PROPERTIES
  IMPORTED_IMPLIB_RELEASE "${_IMPORT_PREFIX}/mitsuba/IlmThread-mitsuba.lib"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/mitsuba/IlmThread-mitsuba.dll"
  )

list(APPEND _cmake_import_check_targets IlmBase::IlmThread )
list(APPEND _cmake_import_check_files_for_IlmBase::IlmThread "${_IMPORT_PREFIX}/mitsuba/IlmThread-mitsuba.lib" "${_IMPORT_PREFIX}/mitsuba/IlmThread-mitsuba.dll" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
