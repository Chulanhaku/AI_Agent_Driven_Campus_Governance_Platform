#pragma once

#include <QObject>

class AppContext;
class ChatPage;

class ChatPresenter : public QObject
{
    Q_OBJECT

public:

    ChatPresenter(AppContext* context,ChatPage* view);

    void send_message(const QString& text);

private:

    AppContext* context;
    ChatPage* view;
};
