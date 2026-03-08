#pragma once

#include <QObject>
#include <QNetworkAccessManager>
#include <QNetworkReply>

class SSEClient : public QObject
{
    Q_OBJECT

public:

    explicit SSEClient(QObject* parent = nullptr);

    void connect_stream(
        const QString& url,
        const QByteArray& body
        );

    void close();

signals:

    void message_chunk(QString text);

    void stream_finished();

    void error(QString msg);

private:

    QNetworkAccessManager manager;

    QNetworkReply* reply = nullptr;

    QByteArray buffer;

    void parse_buffer();
};
