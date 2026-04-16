#include "app_theme.h"

#include "creeper-qt/utility/theme/preset/blue-miku.hh"

namespace
{
creeper::ThemeManager g_theme_manager {
    creeper::kBlueMikuThemePack,
    creeper::ColorMode::LIGHT
};
}

creeper::ThemeManager& app_theme::manager()
{
    return g_theme_manager;
}
