#include "token_manager.h"

TokenManager& TokenManager::instance()
{
    static TokenManager instance;
    return instance;
}

void TokenManager::set_token(const QString& token)
{
    access_token = token;
}

QString TokenManager::token() const
{
    return access_token;
}
