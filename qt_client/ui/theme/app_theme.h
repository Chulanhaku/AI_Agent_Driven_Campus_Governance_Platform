#pragma once

#include "creeper-qt/utility/theme/theme.hh"
#include "creeper-qt/core/application.hh"
#include "creeper-qt/layout/linear.hh"
#include "creeper-qt/layout/mixer.hh"
#include "creeper-qt/layout/scroll.hh"
#include "creeper-qt/layout/stacked.hh"
#include "creeper-qt/utility/material-icon.hh"
#include "creeper-qt/utility/theme/preset/blue-miku.hh"
#include "creeper-qt/utility/theme/preset/gloden-harvest.hh"
#include "creeper-qt/utility/theme/preset/green.hh"
#include "creeper-qt/utility/theme/theme.hh"
#include "creeper-qt/utility/wrapper/layout.hh"
#include "creeper-qt/utility/wrapper/mutable-value.hh"
#include "creeper-qt/utility/wrapper/widget.hh"
#include "creeper-qt/widget/cards/filled-card.hh"
#include "creeper-qt/widget/main-window.hh"
#include "creeper-qt/widget/widget.hh"
#include "creeper-qt/widget/text.hh"
#include "creeper-qt/widget/cards/elevated-card.hh"

class app_theme
{
public:
    static creeper::ThemeManager& manager();
};
