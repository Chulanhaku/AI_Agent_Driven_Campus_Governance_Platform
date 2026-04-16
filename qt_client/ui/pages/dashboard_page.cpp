#include "ui/pages/dashboard_page.h"
#include "ui/theme/app_theme.h"

#include <QVBoxLayout>

dashboard_page::dashboard_page(QWidget* parent)
    : QWidget(parent)
{
    build_ui();
}

void dashboard_page::build_ui()
{
    using namespace creeper;

    namespace wpro = widget::pro;
    namespace lnpro = linear::pro;
    namespace tpro = text::pro;
    namespace capro = card::pro;

    auto& theme_manager = app_theme::manager();

    auto root = new Widget {
        wpro::Layout<Col> {
            lnpro::ContentsMargin { {24, 24, 24, 24} },
            lnpro::Spacing { 16 },

            lnpro::Item<Text> {
                tpro::ThemeManager { theme_manager },
                tpro::Text { "首页" }
            },

            lnpro::Item<ElevatedCard> {
                capro::ThemeManager { theme_manager },
                capro::Radius { 16 },
                capro::Layout<Col> {
                    lnpro::ContentsMargin { {20, 20, 20, 20} },
                    lnpro::Spacing { 8 },

                    lnpro::Item<Text> {
                        tpro::ThemeManager { theme_manager },
                        tpro::Text { "AI 综合校务系统" }
                    },

                    lnpro::Item<Text> {
                        tpro::ThemeManager { theme_manager },
                        tpro::Text { "这里后面放系统概览、未读通知、校园卡余额、快捷入口。" }
                    }
                }
            },

            lnpro::Stretch { 1 }
        }
    };

    auto* host_layout = new QVBoxLayout(this);
    host_layout->setContentsMargins(0, 0, 0, 0);
    host_layout->addWidget(root);
}
