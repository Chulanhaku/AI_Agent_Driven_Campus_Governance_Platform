#pragma once

#include <QObject>

class AppContext;
class LoginWindow;

class LoginPresenter : public QObject
{
    Q_OBJECT

public:
    LoginPresenter(AppContext* context, LoginWindow* view);

    void login(const QString& username,const QString& password);

private:

    AppContext* context;
    LoginWindow* view;
};
