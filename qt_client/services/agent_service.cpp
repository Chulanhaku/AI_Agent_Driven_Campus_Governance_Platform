#include "agent_service.h"

#include "../core/network/sse_client.h"
#include "../core/config/config_manager.h"

#include <QJsonObject>
#include <QJsonDocument>

AgentService::AgentService()
{
    sse = new SSEClient(this);

    connect(
        sse,
        &SSEClient::message_chunk,
        this,
        &AgentService::ai_stream_chunk
        );

    connect(
        sse,
        &SSEClient::stream_finished,
        this,
        &AgentService::ai_stream_finished
        );
}

void AgentService::chat_stream(QString message)
{
    QJsonObject body;

    body["message"] = message;

    QJsonDocument doc(body);

    QString url =
        ConfigManager::instance().api_base_url()
        + "/chat";

    sse->connect_stream(url,doc.toJson());
}
