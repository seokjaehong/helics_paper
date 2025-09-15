#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "HELICS::helics_player" for configuration "Release"
set_property(TARGET HELICS::helics_player APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(HELICS::helics_player PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/bin/helics_player"
  )

list(APPEND _cmake_import_check_targets HELICS::helics_player )
list(APPEND _cmake_import_check_files_for_HELICS::helics_player "${_IMPORT_PREFIX}/bin/helics_player" )

# Import target "HELICS::helics_recorder" for configuration "Release"
set_property(TARGET HELICS::helics_recorder APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(HELICS::helics_recorder PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/bin/helics_recorder"
  )

list(APPEND _cmake_import_check_targets HELICS::helics_recorder )
list(APPEND _cmake_import_check_files_for_HELICS::helics_recorder "${_IMPORT_PREFIX}/bin/helics_recorder" )

# Import target "HELICS::helics_connector" for configuration "Release"
set_property(TARGET HELICS::helics_connector APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(HELICS::helics_connector PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/bin/helics_connector"
  )

list(APPEND _cmake_import_check_targets HELICS::helics_connector )
list(APPEND _cmake_import_check_files_for_HELICS::helics_connector "${_IMPORT_PREFIX}/bin/helics_connector" )

# Import target "HELICS::helics_broker" for configuration "Release"
set_property(TARGET HELICS::helics_broker APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(HELICS::helics_broker PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/bin/helics_broker"
  )

list(APPEND _cmake_import_check_targets HELICS::helics_broker )
list(APPEND _cmake_import_check_files_for_HELICS::helics_broker "${_IMPORT_PREFIX}/bin/helics_broker" )

# Import target "HELICS::helics_broker_server" for configuration "Release"
set_property(TARGET HELICS::helics_broker_server APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(HELICS::helics_broker_server PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/bin/helics_broker_server"
  )

list(APPEND _cmake_import_check_targets HELICS::helics_broker_server )
list(APPEND _cmake_import_check_files_for_HELICS::helics_broker_server "${_IMPORT_PREFIX}/bin/helics_broker_server" )

# Import target "HELICS::helics_app" for configuration "Release"
set_property(TARGET HELICS::helics_app APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(HELICS::helics_app PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/bin/helics_app"
  )

list(APPEND _cmake_import_check_targets HELICS::helics_app )
list(APPEND _cmake_import_check_files_for_HELICS::helics_app "${_IMPORT_PREFIX}/bin/helics_app" )

# Import target "HELICS::helics" for configuration "Release"
set_property(TARGET HELICS::helics APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(HELICS::helics PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libhelics.3.6.1.dylib"
  IMPORTED_SONAME_RELEASE "@rpath/libhelics.3.dylib"
  )

list(APPEND _cmake_import_check_targets HELICS::helics )
list(APPEND _cmake_import_check_files_for_HELICS::helics "${_IMPORT_PREFIX}/lib/libhelics.3.6.1.dylib" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
