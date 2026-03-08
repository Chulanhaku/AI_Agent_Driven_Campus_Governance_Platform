#include "http_client.h"

#include <QNetworkRequest>
#include <QNetworkReply>
#include <QJsonDocument>

HttpClient& HttpClient::instance()
{
    static HttpClient instance;
    return instance;
}

HttpClient::HttpClient()
{
}

void HttpClient::post_json(
    const QString& url,
    const QJsonObject& body,
    std::function<void(QJsonObject)> success,
    std::function<void(QString)> fail
    )
{
    QNetworkRequest request(url);

    request.setHeader(
        QNetworkRequest::ContentTypeHeader,
        "application/json"
        );

    QJsonDocument doc(body);

    auto reply =
        manager.post(request,doc.toJson());

    QObject::connect(reply,&QNetworkReply::finished,[reply,success,fail]()
                     {

                         if(reply->error()!=QNetworkReply::NoError)
                         {
                             fail(reply->errorString());
                             reply->deleteLater();
                             return;
                         }

                         auto data = reply->readAll();

                         QJsonDocument doc =
                             QJsonDocument::fromJson(data);

                         success(doc.object());

                         reply->deleteLater();

                     });
}
