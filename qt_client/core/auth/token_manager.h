#pragma once

#include <QString>

class TokenManager
{
public:

    static TokenManager& instance();

    void set_token(const QString& token);

    QString token() const;

private:

    QString access_token;
};
