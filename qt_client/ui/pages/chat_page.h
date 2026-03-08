#pragma once

#include <QWidget>
#include <QScrollBar>
#include "../widgets/chat_bubble_widget.h"

class AppContext;
class ChatPresenter;

namespace Ui {
class ChatPage;
}

class ChatPage : public QWidget
{
    Q_OBJECT

public:
    explicit ChatPage(AppContext* context,QWidget *parent = nullptr);
    ~ChatPage();

    void add_user_message(const QString& text);
    void add_ai_message(const QString& text);
    void start_ai_stream();
    void append_ai_stream(const QString& token);
    void finish_ai_stream();

private slots:

    void on_send_button_clicked();

private:

    Ui::ChatPage *ui;
    QString current_text;
    AppContext* context;
    ChatPresenter* presenter;
    ChatBubbleWidget* streaming_bubble = nullptr;
};
