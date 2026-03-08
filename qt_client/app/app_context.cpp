#include "app_context.h"

#include "../services/auth_service.h"
#include "../services/agent_service.h"
#include "../services/schedule_service.h"

AppContext::AppContext()
{
    auth_service = std::make_unique<AuthService>();
    agent_service = std::make_unique<AgentService>();
    schedule_service = std::make_unique<ScheduleService>();
}

AppContext::~AppContext()
{
}

AuthService* AppContext::auth()
{
    return auth_service.get();
}

AgentService* AppContext::agent()
{
    return agent_service.get();
}

ScheduleService* AppContext::schedule()
{
    return schedule_service.get();
}
