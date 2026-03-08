#include "chat_page.h"
#include "ui_chat_page.h"

#include "../../presenters/chat_presenter.h"


ChatPage::ChatPage(AppContext* context,QWidget *parent)
    : QWidget(parent),
    ui(new Ui::ChatPage),
    context(context)
{
    ui->setupUi(this);

    presenter = new ChatPresenter(context,this);
}

ChatPage::~ChatPage()
{
    delete presenter;
    delete ui;
}

void ChatPage::on_send_button_clicked()
{
    QString text = ui->input_edit->toPlainText();

    if(text.isEmpty())
        return;

    add_user_message(text);

    presenter->send_message(text);

    ui->input_edit->clear();
}

void ChatPage::add_user_message(const QString& text)
{
    auto bubble = new ChatBubbleWidget(
        text,
        ChatBubbleWidget::bubble_role::user
        );

    ui->chat_layout->addWidget(bubble);
    auto bar = ui->chat_scroll->verticalScrollBar();
    bar->setValue(bar->maximum());
}

void ChatPage::add_ai_message(const QString& text)
{
    auto bubble = new ChatBubbleWidget(
        text,
        ChatBubbleWidget::bubble_role::assistant
        );

    ui->chat_layout->addWidget(bubble);
    auto bar = ui->chat_scroll->verticalScrollBar();
    bar->setValue(bar->maximum());
}

void ChatPage::start_ai_stream()
{
    current_text.clear();
    streaming_bubble = new ChatBubbleWidget(
        "",
        ChatBubbleWidget::bubble_role::assistant
        );

    ui->chat_layout->addWidget(streaming_bubble);
}

void ChatPage::append_ai_stream(const QString& token)
{
    current_text += token;

    streaming_bubble->set_text(current_text);
}

void ChatPage::finish_ai_stream()
{
    streaming_bubble = nullptr;
}
