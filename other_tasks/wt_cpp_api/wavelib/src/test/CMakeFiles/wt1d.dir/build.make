# CMAKE generated file: DO NOT EDIT!
# Generated by "Unix Makefiles" Generator, CMake Version 3.5

# Delete rule output on recipe failure.
.DELETE_ON_ERROR:


#=============================================================================
# Special targets provided by cmake.

# Disable implicit rules so canonical targets will work.
.SUFFIXES:


# Remove some rules from gmake that .SUFFIXES does not remove.
SUFFIXES =

.SUFFIXES: .hpux_make_needs_suffix_list


# Suppress display of executed commands.
$(VERBOSE).SILENT:


# A target that is always out of date.
cmake_force:

.PHONY : cmake_force

#=============================================================================
# Set environment variables for the build.

# The shell in which to execute make rules.
SHELL = /bin/sh

# The CMake executable.
CMAKE_COMMAND = /usr/bin/cmake

# The command to remove a file.
RM = /usr/bin/cmake -E remove -f

# Escaping for special characters.
EQUALS = =

# The top-level source directory on which CMake was run.
CMAKE_SOURCE_DIR = /home/alex/LabGit/ProjectSwiper/other_tasks/wt_cpp_api/wavelib/src/test

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = /home/alex/LabGit/ProjectSwiper/other_tasks/wt_cpp_api/wavelib/src/test

# Include any dependencies generated for this target.
include CMakeFiles/wt1d.dir/depend.make

# Include the progress variables for this target.
include CMakeFiles/wt1d.dir/progress.make

# Include the compile flags for this target's objects.
include CMakeFiles/wt1d.dir/flags.make

CMakeFiles/wt1d.dir/wavelet1d_test.cc.o: CMakeFiles/wt1d.dir/flags.make
CMakeFiles/wt1d.dir/wavelet1d_test.cc.o: wavelet1d_test.cc
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/home/alex/LabGit/ProjectSwiper/other_tasks/wt_cpp_api/wavelib/src/test/CMakeFiles --progress-num=$(CMAKE_PROGRESS_1) "Building CXX object CMakeFiles/wt1d.dir/wavelet1d_test.cc.o"
	/usr/bin/c++   $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -o CMakeFiles/wt1d.dir/wavelet1d_test.cc.o -c /home/alex/LabGit/ProjectSwiper/other_tasks/wt_cpp_api/wavelib/src/test/wavelet1d_test.cc

CMakeFiles/wt1d.dir/wavelet1d_test.cc.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/wt1d.dir/wavelet1d_test.cc.i"
	/usr/bin/c++  $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /home/alex/LabGit/ProjectSwiper/other_tasks/wt_cpp_api/wavelib/src/test/wavelet1d_test.cc > CMakeFiles/wt1d.dir/wavelet1d_test.cc.i

CMakeFiles/wt1d.dir/wavelet1d_test.cc.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/wt1d.dir/wavelet1d_test.cc.s"
	/usr/bin/c++  $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /home/alex/LabGit/ProjectSwiper/other_tasks/wt_cpp_api/wavelib/src/test/wavelet1d_test.cc -o CMakeFiles/wt1d.dir/wavelet1d_test.cc.s

CMakeFiles/wt1d.dir/wavelet1d_test.cc.o.requires:

.PHONY : CMakeFiles/wt1d.dir/wavelet1d_test.cc.o.requires

CMakeFiles/wt1d.dir/wavelet1d_test.cc.o.provides: CMakeFiles/wt1d.dir/wavelet1d_test.cc.o.requires
	$(MAKE) -f CMakeFiles/wt1d.dir/build.make CMakeFiles/wt1d.dir/wavelet1d_test.cc.o.provides.build
.PHONY : CMakeFiles/wt1d.dir/wavelet1d_test.cc.o.provides

CMakeFiles/wt1d.dir/wavelet1d_test.cc.o.provides.build: CMakeFiles/wt1d.dir/wavelet1d_test.cc.o


# Object files for target wt1d
wt1d_OBJECTS = \
"CMakeFiles/wt1d.dir/wavelet1d_test.cc.o"

# External object files for target wt1d
wt1d_EXTERNAL_OBJECTS =

wt1d: CMakeFiles/wt1d.dir/wavelet1d_test.cc.o
wt1d: CMakeFiles/wt1d.dir/build.make
wt1d: libdwt.a
wt1d: CMakeFiles/wt1d.dir/link.txt
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --bold --progress-dir=/home/alex/LabGit/ProjectSwiper/other_tasks/wt_cpp_api/wavelib/src/test/CMakeFiles --progress-num=$(CMAKE_PROGRESS_2) "Linking CXX executable wt1d"
	$(CMAKE_COMMAND) -E cmake_link_script CMakeFiles/wt1d.dir/link.txt --verbose=$(VERBOSE)

# Rule to build all files generated by this target.
CMakeFiles/wt1d.dir/build: wt1d

.PHONY : CMakeFiles/wt1d.dir/build

CMakeFiles/wt1d.dir/requires: CMakeFiles/wt1d.dir/wavelet1d_test.cc.o.requires

.PHONY : CMakeFiles/wt1d.dir/requires

CMakeFiles/wt1d.dir/clean:
	$(CMAKE_COMMAND) -P CMakeFiles/wt1d.dir/cmake_clean.cmake
.PHONY : CMakeFiles/wt1d.dir/clean

CMakeFiles/wt1d.dir/depend:
	cd /home/alex/LabGit/ProjectSwiper/other_tasks/wt_cpp_api/wavelib/src/test && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /home/alex/LabGit/ProjectSwiper/other_tasks/wt_cpp_api/wavelib/src/test /home/alex/LabGit/ProjectSwiper/other_tasks/wt_cpp_api/wavelib/src/test /home/alex/LabGit/ProjectSwiper/other_tasks/wt_cpp_api/wavelib/src/test /home/alex/LabGit/ProjectSwiper/other_tasks/wt_cpp_api/wavelib/src/test /home/alex/LabGit/ProjectSwiper/other_tasks/wt_cpp_api/wavelib/src/test/CMakeFiles/wt1d.dir/DependInfo.cmake --color=$(COLOR)
.PHONY : CMakeFiles/wt1d.dir/depend

