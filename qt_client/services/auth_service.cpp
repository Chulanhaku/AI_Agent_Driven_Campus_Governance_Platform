#include "auth_service.h"

bool AuthService::login(const QString& username,const QString& password)
{
    if(username == "admin" && password == "123")
        return true;

    return false;
}
