#include <QApplication>
#include "app/application.h"

int main(int argc, char *argv[])
{
    QApplication app(argc, argv);

    Application application;
    application.init();

    return app.exec();
}
