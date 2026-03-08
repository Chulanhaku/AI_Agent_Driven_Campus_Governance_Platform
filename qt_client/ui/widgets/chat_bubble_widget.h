#pragma once

#include <QWidget>

class QLabel;
class QHBoxLayout;

class ChatBubbleWidget : public QWidget
{
    Q_OBJECT

public:

    enum class bubble_role
    {
        user,
        assistant
    };

    ChatBubbleWidget(const QString& text,
                     bubble_role role,
                     QWidget* parent = nullptr);

    void set_text(const QString& text);

private:

    QLabel* avatar;
    QLabel* text_label;

    QWidget* bubble_container;

    QHBoxLayout* root_layout;

    bubble_role role;

    void build_ui();
    void apply_style();
};
