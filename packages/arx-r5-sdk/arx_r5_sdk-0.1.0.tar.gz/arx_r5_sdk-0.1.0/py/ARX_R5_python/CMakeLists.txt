cmake_minimum_required(VERSION 3.18)
project(arx_r5_python)

set(PYBIND11_FINDPYTHON ON)
find_package(pybind11 REQUIRED)

include_directories(cpp/src)
include_directories(cpp/lib)
include_directories(cpp/lib/arx_r5_src/include)
include_directories(cpp/lib/arx_hardware_interface/include)

pybind11_add_module(${PROJECT_NAME} cpp/src/single_arm_interface.cpp)
pybind11_add_module(kinematic_solver cpp/src/kinematic_solver.cpp)

if (CMAKE_SYSTEM_PROCESSOR MATCHES "aarch64")
    set(DEPEND_LIB "${CMAKE_CURRENT_SOURCE_DIR}/src/arx_r5_sdk/lib/libarx_r5_src-arm64.so")
else()
    set(DEPEND_LIB "${CMAKE_CURRENT_SOURCE_DIR}/src/arx_r5_sdk/lib/libarx_r5_src.so")
endif()

target_link_libraries(${PROJECT_NAME} PUBLIC ${DEPEND_LIB} pybind11::module)
target_link_libraries(kinematic_solver PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/src/arx_r5_sdk/lib/libkinematic_solver.so pybind11::module)
