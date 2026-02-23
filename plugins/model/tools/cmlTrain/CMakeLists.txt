cmake_minimum_required(VERSION 3.10)

project(cmlTrain)

include_directories(
    ../../../../core/include
    ../../../../plugins
    ../../../../libs/build/ssimongo/include
    ../../../../libs/build/ssimongo/mongoc/include
    ../../../../libs/build/ssimongo/libbson/include
)

# Locate the source file. It seems it might be in this directory or misplaced in build directory previously.
# Based on earlier context, we will assume it should be here.
# If the file is physically in plugins/model/build/tools/cmltrain_Main.cpp, we might need to copy it or point to it.
# However, for a clean migration, we should expect it in source/ or current dir.
# Let's list the source files as if they are in 'source' subdirectory or current dir.
# The previous cmltrain_Main.cpp edits suggested it was the main file.

set(SRC_FILES
    # source/cmltrain_Main.cpp  <-- Assuming standard structure ?
    # Or just current directory if it's a simple tool.
    # Let's check listing of plugins/model/tools/cmlTrain if it doesn't exist yet.
)

# Since I cannot see cmlTrain folder yet (it was missing in list_dir of tools),
# I assume I need to CREATE the folder and put the source there, 
# OR point to where it is.
# The user was editing plugins/model/build/tools/cmltrain_Main.cpp.
# I should probably MOVE that file to plugins/model/tools/cmlTrain/cmltrain_Main.cpp
# but I cannot move files easily without potential data loss if I overwrite.

# For now, I will create the CMakeLists.txt and assume source is 'cmltrain_Main.cpp' in the same folder.
# I will need to write the content of the modified cmltrain_Main.cpp to this new location.

add_executable(ssicmltrain cmltrain_Main.cpp)

target_link_libraries(ssicmltrain 
    ssimodel 
    ssicml
    ssimongo 
    ssiopensmile 
    ssi
)

install(TARGETS ssicmltrain DESTINATION ${SSI_INSTALL}/${SSI_PLATFORM}/${SSI_COMPILER})
