#pragma once

#include <QString>
#include <QJsonObject>

class ConfigManager
{
public:

    static ConfigManager& instance();

    void load(const QString& path);

    QString api_base_url() const;

    int http_timeout() const;

private:

    ConfigManager() = default;

    QJsonObject config_json;
};
