#pragma once

#include <memory>

class AuthService;
class AgentService;
class ScheduleService;

class AppContext
{
public:
    AppContext();
    ~AppContext();

    AuthService* auth();
    AgentService* agent();
    ScheduleService* schedule();

private:
    std::unique_ptr<AuthService> auth_service;
    std::unique_ptr<AgentService> agent_service;
    std::unique_ptr<ScheduleService> schedule_service;
};
