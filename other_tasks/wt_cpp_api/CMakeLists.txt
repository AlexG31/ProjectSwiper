include(CheckCXXCompilerFlag)
CHECK_CXX_COMPILER_FLAG("-std=c++11" COMPILER_SUPPORTS_CXX11)
CHECK_CXX_COMPILER_FLAG("-std=c++0x" COMPILER_SUPPORTS_CXX0X)
if(COMPILER_SUPPORTS_CXX11)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")
elseif(COMPILER_SUPPORTS_CXX0X)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++0x")
else()
        message(STATUS "The compiler ${CMAKE_CXX_COMPILER} has no C++11 support. Please use a different C++ compiler.")
endif()

cmake_minimum_required(VERSION 3.5)

LINK_DIRECTORIES(/usr/lib/x86_64-linux-gnu)

add_library(dwt wavelib/src/shared/wavedec_api.cc ./wavelet2d.cc ./wavelet_udfs.cc ./DTCWT.cc ./Qshift.cc)

add_library(KPD_pt call_simple_function/QRS_detection.cc call_simple_function/rdivide.cc call_simple_function/call_simple_function_emxutil.cc call_simple_function/mean.cc call_simple_function/power.cc call_simple_function/call_simple_function_emxAPI.cc call_simple_function/gaussian_function.cc call_simple_function/call_simple_function_terminate.cc call_simple_function/rtGetInf.cc call_simple_function/abs.cc call_simple_function/rt_nonfinite.cc call_simple_function/eml_sort.cc call_simple_function/rtGetNaN.cc call_simple_function/call_simple_function_initialize.cc call_simple_function/T_detection.cc call_simple_function/floor.cc call_simple_function/call_simple_function.cc call_simple_function/sum.cc)

add_executable(wt_run wavelet-test.cc)
add_executable(wt_detect wt_detect.cc)

target_link_libraries(wt_run dwt)
target_link_libraries(wt_run fftw3)

target_link_libraries(wt_detect dwt)
target_link_libraries(wt_detect KPD_pt)
target_link_libraries(wt_detect m)
target_link_libraries(wt_detect fftw3)
