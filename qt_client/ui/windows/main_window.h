#pragma once

#include <QMainWindow>

class AppContext;

namespace Ui {
class MainWindow;
}

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    explicit MainWindow(AppContext* context,QWidget *parent = nullptr);
    ~MainWindow();

private slots:

    void on_dashboard_clicked();
    void on_chat_clicked();
    void on_schedule_clicked();
    void on_leave_clicked();
    void on_card_clicked();

private:

    Ui::MainWindow *ui;

    AppContext* context;
};
