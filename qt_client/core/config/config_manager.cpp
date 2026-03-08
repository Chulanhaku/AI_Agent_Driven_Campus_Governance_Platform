#include "config_manager.h"

#include <QFile>
#include <QJsonDocument>

ConfigManager& ConfigManager::instance()
{
    static ConfigManager instance;
    return instance;
}

void ConfigManager::load(const QString& path)
{
    QFile file(path);

    if(!file.open(QIODevice::ReadOnly))
        return;

    auto data = file.readAll();

    QJsonDocument doc = QJsonDocument::fromJson(data);

    config_json = doc.object();
}

QString ConfigManager::api_base_url() const
{
    return config_json["api_base_url"].toString();
}

int ConfigManager::http_timeout() const
{
    return config_json["timeout"].toInt(30);
}
