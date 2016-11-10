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
LINK_DIRECTORIES(/home/alex/LabGit/ProjectSwiper/other_tasks/call_simple_function)

add_library(dwt ./wavelet2d.cc ./wavelet_udfs.cc ./DTCWT.cc ./Qshift.cc)

add_library(kpd abs.cc call_simple_function.cc call_simple_function_data.cc call_simple_function_emxAPI.cc call_simple_function_emxutil.cc call_simple_function_initialize.cc call_simple_function_terminate.cc eml_rand.cc eml_rand_mcg16807_stateful.cc eml_rand_mt19937ar_stateful.cc eml_rand_shr3cong_stateful.cc eml_sort.cc floor.cc gaussian_function.cc KPD.cc mean.cc power.cc QRS_detection.cc rand.cc rdivide.cc rtGetInf.cc rtGetNaN.cc rt_nonfinite.cc simple_function.cc sum.cc T_detection.cc)

add_executable(wt_run wavelet-test.cc)
add_executable(wt_detect wt_detect.cc)

target_link_libraries(wt_run dwt)
target_link_libraries(wt_run fftw3)

target_link_libraries(wt_detect dwt)
target_link_libraries(wt_detect kpd)
target_link_libraries(wt_detect fftw3)
