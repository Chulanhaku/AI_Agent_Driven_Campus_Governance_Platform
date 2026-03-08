#pragma once

#include <QObject>
#include <QNetworkAccessManager>
#include <QJsonObject>

class HttpClient : public QObject
{
    Q_OBJECT

public:

    static HttpClient& instance();

    void post_json(
        const QString& url,
        const QJsonObject& body,
        std::function<void(QJsonObject)> success,
        std::function<void(QString)> fail
        );

private:

    HttpClient();

    QNetworkAccessManager manager;
};
