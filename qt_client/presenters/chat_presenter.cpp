#include "chat_presenter.h"

#include "../app/app_context.h"
#include "../services/agent_service.h"
#include "../ui/pages/chat_page.h"

ChatPresenter::ChatPresenter(AppContext* context,ChatPage* view)
{
    this->context = context;
    this->view = view;
    connect(
        context->agent(),
        &AgentService::ai_stream_chunk,
        view,
        &ChatPage::append_ai_stream
        );

    connect(
        context->agent(),
        &AgentService::ai_stream_finished,
        view,
        &ChatPage::finish_ai_stream
        );
}

void ChatPresenter::send_message(const QString& text)
{
    view->start_ai_stream();

    context->agent()->chat_stream(text);
}
