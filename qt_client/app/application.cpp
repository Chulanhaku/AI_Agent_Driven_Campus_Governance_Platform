#include "application.h"
#include "app_context.h"

#include "../ui/windows/login_window.h"

Application::Application()
{
}

Application::~Application()
{
}

void Application::init()
{
    context = std::make_unique<AppContext>();

    login_window = std::make_unique<LoginWindow>(context.get());
    login_window->show();
}
