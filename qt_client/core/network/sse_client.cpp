#include "sse_client.h"

#include <QNetworkRequest>
#include <QJsonDocument>

SSEClient::SSEClient(QObject* parent)
    : QObject(parent)
{
}

void SSEClient::connect_stream(
    const QString& url,
    const QByteArray& body
    )
{
    QNetworkRequest request(url);

    request.setHeader(
        QNetworkRequest::ContentTypeHeader,
        "application/json"
        );

    request.setRawHeader("Accept","text/event-stream");

    reply = manager.post(request,body);

    connect(reply,&QNetworkReply::readyRead,this,[this]()
            {
                buffer += reply->readAll();
                parse_buffer();
            });

    connect(reply,&QNetworkReply::finished,this,[this]()
            {
                emit stream_finished();
            });

    connect(reply,
            &QNetworkReply::errorOccurred,
            this,
            [this](QNetworkReply::NetworkError)
            {
                emit error(reply->errorString());
            });
}

void SSEClient::close()
{
    if(reply)
    {
        reply->abort();
        reply->deleteLater();
        reply = nullptr;
    }
}

void SSEClient::parse_buffer()
{
    while(true)
    {
        int pos = buffer.indexOf("\n");

        if(pos < 0)
            return;

        QByteArray line = buffer.left(pos).trimmed();

        buffer.remove(0,pos+1);

        if(line.startsWith("data:"))
        {
            QByteArray payload = line.mid(5).trimmed();

            QString text = QString::fromUtf8(payload);

            if(text == "[DONE]")
            {
                emit stream_finished();
                return;
            }

            emit message_chunk(text);
        }
    }
}
