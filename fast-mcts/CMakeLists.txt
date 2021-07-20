cmake_minimum_required(VERSION 3.0 FATAL_ERROR)
project(TCC VERSION 1.0)

set(CMAKE_CXX_FLAGS "-Wall -Wextra")
set(CMAKE_CXX_FLAGS_RELEASE "-O3")

find_package(Torch REQUIRED)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${TORCH_CXX_FLAGS}")

file(GLOB_RECURSE SOURCES CONFIGURE_DEPENDS "src/*.cpp")
file(GLOB_RECURSE HEADERS CONFIGURE_DEPENDS "include/*.hpp")

file(GLOB_RECURSE EXAMPLES CONFIGURE_DEPENDS "examples/*.cpp")

include_directories("./include")

foreach(_exampleFile ${EXAMPLES})
    get_filename_component(barename ${_exampleFile} NAME)
    get_filename_component(executableName ${barename} NAME_WE)

    add_executable(${executableName} ${_exampleFile} ${SOURCES})
    target_link_libraries(${executableName} "${TORCH_LIBRARIES}")
    set_property(TARGET ${executableName} PROPERTY CXX_STANDARD 20)
endforeach()




