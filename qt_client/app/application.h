#pragma once

#include <QObject>
#include <memory>

class LoginWindow;
class AppContext;

class Application : public QObject
{
    Q_OBJECT

public:
    Application();
    ~Application();

    void init();

private:
    std::unique_ptr<AppContext> context;
    std::unique_ptr<LoginWindow> login_window;
};
