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

add_library(KPD_pt QRS_detection.c rdivide.c call_simple_function_emxutil.c mean.c power.c call_simple_function_emxAPI.c gaussian_function.c call_simple_function_terminate.c rtGetInf.c abs.c rt_nonfinite.c eml_sort.c rtGetNaN.c call_simple_function_initialize.c T_detection.c floor.c call_simple_function.c sum.c )

add_executable(wt_detect call_simple_function.c)

#target_link_libraries(wt_detect dwt)
target_link_libraries(wt_detect KPD_pt)
target_link_libraries(wt_detect m)
#target_link_libraries(wt_detect m)
target_link_libraries(wt_detect fftw3)

