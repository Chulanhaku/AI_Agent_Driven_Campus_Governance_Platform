#include "login_presenter.h"
#include "../app/app_context.h"
#include "../services/auth_service.h"

LoginPresenter::LoginPresenter(AppContext* context, LoginWindow* view)
{
    this->context = context;
    this->view = view;
}

void LoginPresenter::login(const QString& username,const QString& password)
{
    auto auth = context->auth();

    bool ok = auth->login(username,password);

    if(ok)
    {
        // TODO: open main window
    }
}
