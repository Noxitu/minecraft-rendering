cmake_minimum_required(VERSION 3.10)
project(RayCasting LANGUAGES CXX)

find_package(OpenMP REQUIRED)

add_library("${PROJECT_NAME}" SHARED src/c_api.cpp)
target_link_libraries("${PROJECT_NAME}" PRIVATE OpenMP::OpenMP_CXX)