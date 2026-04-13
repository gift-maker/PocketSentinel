cmake_minimum_required(VERSION 3.14)    # CMake最低版本要求
project(masker)                          # 项目名称
set(CMAKE_CXX_STANDARD 17)              # 使用C++17标准

find_package(OpenSSL REQUIRED)           # 找OpenSSL库，找不到就报错

add_executable(masker src/main.cpp)      # 用main.cpp编译出masker可执行文件
target_link_libraries(masker OpenSSL::Crypto)  # 链接OpenSSL加密库

