#pragma once

#include <QString>

class Logger
{
public:

    static void info(const QString& msg);

    static void error(const QString& msg);

    static void debug(const QString& msg);

private:

    static void write(const QString& level,const QString& msg);
};
