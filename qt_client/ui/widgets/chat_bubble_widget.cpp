#include "chat_bubble_widget.h"

#include <QHBoxLayout>
#include <QLabel>
#include <QPixmap>

ChatBubbleWidget::ChatBubbleWidget(
    const QString& text,
    bubble_role role,
    QWidget* parent
    )
    : QWidget(parent), role(role)
{
    build_ui();
    apply_style();
    set_text(text);
}

void ChatBubbleWidget::build_ui()
{
    root_layout = new QHBoxLayout(this);

    avatar = new QLabel;
    avatar->setFixedSize(32,32);

    bubble_container = new QWidget;
    auto bubble_layout = new QVBoxLayout(bubble_container);

    text_label = new QLabel;
    text_label->setWordWrap(true);

    bubble_layout->addWidget(text_label);

    if(role == bubble_role::assistant)
    {
        root_layout->addWidget(avatar);
        root_layout->addWidget(bubble_container);
        root_layout->addStretch();
    }
    else
    {
        root_layout->addStretch();
        root_layout->addWidget(bubble_container);
        root_layout->addWidget(avatar);
    }
}

void ChatBubbleWidget::apply_style()
{
    if(role == bubble_role::assistant)
    {
        bubble_container->setStyleSheet(
            "background:#F0F0F0;"
            "border-radius:8px;"
            "padding:8px;"
            );
    }
    else
    {
        bubble_container->setStyleSheet(
            "background:#4CAF50;"
            "color:white;"
            "border-radius:8px;"
            "padding:8px;"
            );
    }
}

void ChatBubbleWidget::set_text(const QString& text)
{
    text_label->setText(text);
}
