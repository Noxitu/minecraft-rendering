cmake_minimum_required(VERSION 3.10)
project(RayCasting LANGUAGES CXX)

add_library("${PROJECT_NAME}" SHARED src/c_api.cpp)