#pragma once

#include <QMainWindow>
#include "creeper-qt/layout/stacked.hh"


class main_window : public QMainWindow
{
    Q_OBJECT

public:
    explicit main_window(QWidget* parent = nullptr);

private:
    creeper::Stacked* page_stack_ = nullptr;

    void build_ui();
    QWidget* build_placeholder_page(const QString& title, const QString& description);
};
