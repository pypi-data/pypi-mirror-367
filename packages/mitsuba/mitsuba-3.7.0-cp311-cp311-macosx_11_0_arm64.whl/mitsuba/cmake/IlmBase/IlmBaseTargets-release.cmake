#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "IlmBase::Half" for configuration "Release"
set_property(TARGET IlmBase::Half APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(IlmBase::Half PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/mitsuba/libHalf-mitsuba.dylib"
  IMPORTED_SONAME_RELEASE "@rpath/libHalf-mitsuba.dylib"
  )

list(APPEND _cmake_import_check_targets IlmBase::Half )
list(APPEND _cmake_import_check_files_for_IlmBase::Half "${_IMPORT_PREFIX}/mitsuba/libHalf-mitsuba.dylib" )

# Import target "IlmBase::Iex" for configuration "Release"
set_property(TARGET IlmBase::Iex APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(IlmBase::Iex PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/mitsuba/libIex-mitsuba.dylib"
  IMPORTED_SONAME_RELEASE "@rpath/libIex-mitsuba.dylib"
  )

list(APPEND _cmake_import_check_targets IlmBase::Iex )
list(APPEND _cmake_import_check_files_for_IlmBase::Iex "${_IMPORT_PREFIX}/mitsuba/libIex-mitsuba.dylib" )

# Import target "IlmBase::IexMath" for configuration "Release"
set_property(TARGET IlmBase::IexMath APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(IlmBase::IexMath PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/mitsuba/libIexMath-mitsuba.dylib"
  IMPORTED_SONAME_RELEASE "@rpath/libIexMath-mitsuba.dylib"
  )

list(APPEND _cmake_import_check_targets IlmBase::IexMath )
list(APPEND _cmake_import_check_files_for_IlmBase::IexMath "${_IMPORT_PREFIX}/mitsuba/libIexMath-mitsuba.dylib" )

# Import target "IlmBase::Imath" for configuration "Release"
set_property(TARGET IlmBase::Imath APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(IlmBase::Imath PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/mitsuba/libImath-mitsuba.dylib"
  IMPORTED_SONAME_RELEASE "@rpath/libImath-mitsuba.dylib"
  )

list(APPEND _cmake_import_check_targets IlmBase::Imath )
list(APPEND _cmake_import_check_files_for_IlmBase::Imath "${_IMPORT_PREFIX}/mitsuba/libImath-mitsuba.dylib" )

# Import target "IlmBase::IlmThread" for configuration "Release"
set_property(TARGET IlmBase::IlmThread APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(IlmBase::IlmThread PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/mitsuba/libIlmThread-mitsuba.dylib"
  IMPORTED_SONAME_RELEASE "@rpath/libIlmThread-mitsuba.dylib"
  )

list(APPEND _cmake_import_check_targets IlmBase::IlmThread )
list(APPEND _cmake_import_check_files_for_IlmBase::IlmThread "${_IMPORT_PREFIX}/mitsuba/libIlmThread-mitsuba.dylib" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
