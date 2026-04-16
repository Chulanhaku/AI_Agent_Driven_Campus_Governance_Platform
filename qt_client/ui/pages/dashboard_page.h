#pragma once

#include <QWidget>

class dashboard_page : public QWidget
{
    Q_OBJECT

public:
    explicit dashboard_page(QWidget* parent = nullptr);

private:
    void build_ui();
};
