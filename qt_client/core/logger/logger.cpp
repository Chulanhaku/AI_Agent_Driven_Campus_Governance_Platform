#include "logger.h"

#include <QDateTime>
#include <QDebug>

void Logger::info(const QString& msg)
{
    write("INFO",msg);
}

void Logger::error(const QString& msg)
{
    write("ERROR",msg);
}

void Logger::debug(const QString& msg)
{
    write("DEBUG",msg);
}

void Logger::write(const QString& level,const QString& msg)
{
    QString line =
        QDateTime::currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
        + " [" + level + "] "
        + msg;

    qDebug().noquote() << line;
}
