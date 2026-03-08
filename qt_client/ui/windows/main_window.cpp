#include "main_window.h"
#include "ui_main_window.h"

#include "../../app/app_context.h"

MainWindow::MainWindow(AppContext* context,QWidget *parent)
    : QMainWindow(parent),
    ui(new Ui::MainWindow),
    context(context)
{
    ui->setupUi(this);

    ui->stackedWidget->setCurrentIndex(0);
}

MainWindow::~MainWindow()
{
    delete ui;
}

void MainWindow::on_dashboard_clicked()
{
    ui->stackedWidget->setCurrentIndex(0);
}

void MainWindow::on_chat_clicked()
{
    ui->stackedWidget->setCurrentIndex(1);
}

void MainWindow::on_schedule_clicked()
{
    ui->stackedWidget->setCurrentIndex(2);
}

void MainWindow::on_leave_clicked()
{
    ui->stackedWidget->setCurrentIndex(3);
}

void MainWindow::on_card_clicked()
{
    ui->stackedWidget->setCurrentIndex(4);
}
