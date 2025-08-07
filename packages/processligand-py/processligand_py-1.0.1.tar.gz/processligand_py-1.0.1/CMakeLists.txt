# CMakeLists.txt

cmake_minimum_required(VERSION 3.15)
project(processligand_builder C)

include(FetchContent)

FetchContent_Declare(
  processligand_repo
  GIT_REPOSITORY https://github.com/NRGlab/Process_Ligand.git
  GIT_TAG        cmake
)

set(CMAKE_BUILD_TYPE Release)
set(BUILD_STATIC_EXECUTABLE ON)

FetchContent_MakeAvailable(processligand_repo)

set(PROCESSLIGAND_EXECUTABLE $<TARGET_FILE:ProcessLigand>)

install(PROGRAMS ${PROCESSLIGAND_EXECUTABLE}
    DESTINATION ${CMAKE_INSTALL_PREFIX}/bin
)

install(FILES
    ${CMAKE_CURRENT_SOURCE_DIR}/processligandpy/__init__.py
    ${CMAKE_CURRENT_SOURCE_DIR}/processligandpy/processligand_wrapper.py
    DESTINATION ${CMAKE_INSTALL_PREFIX}
)