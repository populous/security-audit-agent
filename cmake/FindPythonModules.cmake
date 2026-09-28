# cmake/FindPythonModules.cmake
# Find Python modules using pip

function(find_python_module module_name)
    set(options REQUIRED)
    set(oneValueArgs)
    set(multiValueArgs)
    cmake_parse_arguments(FIND_PYTHON_MODULE "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})

    # Python3_EXECUTABLE 이 정의되어 있는지 확인
    if(NOT Python3_EXECUTABLE)
        find_package(Python3 COMPONENTS Interpreter REQUIRED)
    endif()

    # 모듈 설치 여부 확인
    execute_process(
        COMMAND ${Python3_EXECUTABLE} -c "import ${module_name}" RESULT_VARIABLE result
        OUTPUT_QUIET ERROR_QUIET
    )

    if(result EQUAL 0)
        set(${module_name}_FOUND TRUE PARENT_SCOPE)
        message(STATUS "Found Python module: ${module_name}")
    else()
        if(FIND_PYTHON_MODULE_REQUIRED)
            message(FATAL_ERROR "Python module '${module_name}' not found. Install with: pip install ${module_name}")
        else()
            set(${module_name}_FOUND FALSE PARENT_SCOPE)
            message(WARNING "Python module '${module_name}' not found")
        endif()
    endif()
endfunction()
