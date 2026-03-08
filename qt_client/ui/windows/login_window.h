#pragma once

#include <QMainWindow>

class AppContext;
class LoginPresenter;

namespace Ui {
class LoginWindow;
}

class LoginWindow : public QMainWindow
{
    Q_OBJECT

public:
    explicit LoginWindow(AppContext* context, QWidget *parent = nullptr);
    ~LoginWindow();

private slots:

    void on_login_button_clicked();

private:

    Ui::LoginWindow *ui;

    AppContext* context;
    LoginPresenter* presenter;
};
