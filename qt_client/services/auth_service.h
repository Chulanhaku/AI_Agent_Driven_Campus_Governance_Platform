#pragma once

#include <QString>

class AuthService
{
public:

    bool login(const QString& username,const QString& password);
};
