#pragma once

#include <QJsonObject>

class JsonUtils
{
public:

    static QString get_string(
        const QJsonObject& obj,
        const QString& key
        );

    static int get_int(
        const QJsonObject& obj,
        const QString& key
        );
};
