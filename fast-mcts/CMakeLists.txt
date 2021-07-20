cmake_minimum_required(VERSION 3.0 FATAL_ERROR)
project(TCC VERSION 1.0)

set(CMAKE_CXX_FLAGS "-Wall -Wextra")
set(CMAKE_CXX_FLAGS_RELEASE "-O3")

find_package(Torch REQUIRED)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${TORCH_CXX_FLAGS}")

file(GLOB SOURCES
    ./*.hpp
    ./*.cpp
)

add_executable(fast-mcts ${SOURCES})
target_link_libraries(fast-mcts "${TORCH_LIBRARIES}")
set_property(TARGET fast-mcts PROPERTY CXX_STANDARD 20)


