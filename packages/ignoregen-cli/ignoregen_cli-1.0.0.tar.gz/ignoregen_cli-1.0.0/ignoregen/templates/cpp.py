"""C++ .gitignore template."""

CPP_TEMPLATE = {
    'name': 'C++',
    'content': '''# Compiled Object files
*.slo
*.lo
*.o
*.obj

# Precompiled Headers
*.gch
*.pch

# Compiled Dynamic libraries
*.so
*.dylib
*.dll

# Fortran module files
*.mod
*.smod

# Compiled Static libraries
*.lai
*.la
*.a
*.lib

# Executables
*.exe
*.out
*.app

# Build directories
build/
Build/
debug/
Debug/
release/
Release/
bin/
obj/

# CMake
CMakeCache.txt
CMakeFiles
CMakeScripts
Testing
Makefile
cmake_install.cmake
install_manifest.txt
compile_commands.json
CTestTestfile.cmake
_deps

# Visual Studio
.vs/
*.vcxproj.user
*.vspscc
*.vssscc
.builds
*.pidb
*.svclog
*.scc

# Code::Blocks
*.depend
*.layout
*.cbp

# Dev-C++
*.dev

# QtCreator
*.pro.user
*.pro.user.*
*.qbs.user
*.qbs.user.*
*.moc
*.qrc
*.ui

# IDEs
.vscode/
.idea/

# OS generated files
.DS_Store
Thumbs.db'''
}