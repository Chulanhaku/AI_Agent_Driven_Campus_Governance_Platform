#include "login_window.h"
#include "ui_login_window.h"

#include "../../presenters/login_presenter.h"
#include "../../app/app_context.h"

LoginWindow::LoginWindow(AppContext* context, QWidget *parent)
    : QMainWindow(parent),
    ui(new Ui::LoginWindow),
    context(context)
{
    ui->setupUi(this);

    presenter = new LoginPresenter(context, this);
}

LoginWindow::~LoginWindow()
{
    delete presenter;
    delete ui;
}

void LoginWindow::on_login_button_clicked()
{
    QString username = ui->username_edit->text();
    QString password = ui->password_edit->text();

    presenter->login(username, password);
}
