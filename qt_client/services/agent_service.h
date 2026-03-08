#pragma once

#include <QObject>

class SSEClient;

class AgentService : public QObject
{
    Q_OBJECT

public:

    AgentService();

    void chat_stream(QString message);

signals:

    void ai_stream_chunk(QString text);

    void ai_stream_finished();

private:

    SSEClient* sse;
};
