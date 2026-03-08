cmake_minimum_required(VERSION 3.16)

project(qt_client VERSION 0.1 LANGUAGES CXX)

set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(QT NAMES Qt6 Qt5 REQUIRED COMPONENTS Widgets Network)
find_package(Qt${QT_VERSION_MAJOR} REQUIRED COMPONENTS Widgets Network)

set(PROJECT_SOURCES
        main.cpp



)

if(${QT_VERSION_MAJOR} GREATER_EQUAL 6)
    qt_add_executable(qt_client
        MANUAL_FINALIZATION
        ${PROJECT_SOURCES}
        app/application.h app/application.cpp
        app/app_context.h app/app_context.cpp
        ui/windows/login_window.h ui/windows/login_window.cpp ui/windows/login_window.ui
        presenters/login_presenter.h presenters/login_presenter.cpp
        services/auth_service.h services/auth_service.cpp
        ui/windows/main_window.h ui/windows/main_window.cpp ui/windows/main_window.ui
        ui/pages/chat_page.h ui/pages/chat_page.cpp ui/pages/chat_page.ui
        presenters/chat_presenter.h presenters/chat_presenter.cpp
        services/agent_service.h services/agent_service.cpp
        ui/widgets/chat_bubble_widget.h ui/widgets/chat_bubble_widget.cpp ui/widgets/chat_bubble_widget.ui
        core/config/config_manager.h core/config/config_manager.cpp
        core/logger/logger.h core/logger/logger.cpp
        core/network/http_client.h core/network/http_client.cpp
        core/auth/token_manager.h core/auth/token_manager.cpp
        core/utils/json_utils.h core/utils/json_utils.cpp
        core/network/sse_client.h core/network/sse_client.cpp

    )
# Define target properties for Android with Qt 6 as:
#    set_property(TARGET qt_client APPEND PROPERTY QT_ANDROID_PACKAGE_SOURCE_DIR
#                 ${CMAKE_CURRENT_SOURCE_DIR}/android)
# For more information, see https://doc.qt.io/qt-6/qt-add-executable.html#target-creation
else()
    if(ANDROID)
        add_library(qt_client SHARED
            ${PROJECT_SOURCES}
        )
# Define properties for Android with Qt 5 after find_package() calls as:
#    set(ANDROID_PACKAGE_SOURCE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/android")
    else()
        add_executable(qt_client
            ${PROJECT_SOURCES}
        )
    endif()
endif()

target_link_libraries(qt_client PRIVATE
    Qt${QT_VERSION_MAJOR}::Widgets
    Qt${QT_VERSION_MAJOR}::Network
)

# Qt for iOS sets MACOSX_BUNDLE_GUI_IDENTIFIER automatically since Qt 6.1.
# If you are developing for iOS or macOS you should consider setting an
# explicit, fixed bundle identifier manually though.
if(${QT_VERSION} VERSION_LESS 6.1.0)
  set(BUNDLE_ID_OPTION MACOSX_BUNDLE_GUI_IDENTIFIER com.example.qt_client)
endif()
set_target_properties(qt_client PROPERTIES
    ${BUNDLE_ID_OPTION}
    MACOSX_BUNDLE_BUNDLE_VERSION ${PROJECT_VERSION}
    MACOSX_BUNDLE_SHORT_VERSION_STRING ${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}
    MACOSX_BUNDLE TRUE
    WIN32_EXECUTABLE TRUE
)

include(GNUInstallDirs)
install(TARGETS qt_client
    BUNDLE DESTINATION .
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)

if(QT_VERSION_MAJOR EQUAL 6)
    qt_finalize_executable(qt_client)
endif()
