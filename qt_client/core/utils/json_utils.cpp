#include "json_utils.h"

QString JsonUtils::get_string(
    const QJsonObject& obj,
    const QString& key
    )
{
    return obj.value(key).toString();
}

int JsonUtils::get_int(
    const QJsonObject& obj,
    const QString& key
    )
{
    return obj.value(key).toInt();
}
