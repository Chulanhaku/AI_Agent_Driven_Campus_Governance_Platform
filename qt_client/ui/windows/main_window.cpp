#include "ui/windows/main_window.h"
#include "ui/theme/app_theme.h"
#include "ui/pages/dashboard_page.h"
#include "creeper-qt/widget/buttons/button.hh"
#include "creeper-qt/widget/buttons/icon-button.hh"
#include "creeper-qt/widget/buttons/filled-button.hh"

#include <QVBoxLayout>

main_window::main_window(QWidget* parent)
    : QMainWindow(parent)
{
    build_ui();
}

QWidget* main_window::build_placeholder_page(const QString& title, const QString& description)
{
    using namespace creeper;

    namespace wpro = widget::pro;
    namespace lnpro = linear::pro;
    namespace tpro = text::pro;

    auto& theme_manager = app_theme::manager();

    return new Widget {
        wpro::Layout<Col> {
            lnpro::ContentsMargin { {24, 24, 24, 24} },
            lnpro::Spacing { 12 },

            lnpro::Item<Text> {
                tpro::ThemeManager { theme_manager },
                tpro::Text { title }
            },

            lnpro::Item<Text> {
                tpro::ThemeManager { theme_manager },
                tpro::Text { description },
                tpro::WordWrap { true }
            },

            lnpro::Stretch { 1 }
        }
    };
}

void main_window::build_ui()
{
    using namespace creeper;

    namespace wpro = widget::pro;
    namespace lnpro = linear::pro;
    namespace bpro = button::pro;
    namespace ibpro = icon_button::pro;
    namespace stpro = stacked::pro;
    namespace capro = card::pro;

    auto& theme_manager = app_theme::manager();

    page_stack_ = new Stacked {
        stpro::Index { 0 },
        stpro::Item { new dashboard_page {} },
        stpro::Item { build_placeholder_page("聊天", "这里后面接 /api/v1/chat/send、/history、/confirm、/tool-logs") },
        stpro::Item { build_placeholder_page("课表", "这里后面接 /api/v1/schedule/me") },
        stpro::Item { build_placeholder_page("校园卡", "这里后面接 /api/v1/campus-card/balance") },
        stpro::Item { build_placeholder_page("请假", "这里后面接 /api/v1/leave/me") },
        stpro::Item { build_placeholder_page("通知", "这里后面接 /api/v1/notifications/me") },
        stpro::Item { build_placeholder_page("审计", "这里后面接 /api/v1/audit/me") }
    };

    auto* root = new Widget {
        wpro::Layout<Row> {
            lnpro::ContentsMargin { {12, 12, 12, 12} },
            lnpro::Spacing { 12 },

            lnpro::Item<ElevatedCard> {
                capro::ThemeManager { theme_manager },
                capro::Radius { 20 },
                wpro::FixedWidth { 220 },

                capro::Layout<Col> {
                    lnpro::ContentsMargin { {16, 16, 16, 16} },
                    lnpro::Spacing { 10 },

                    lnpro::Item<FilledButton> {
                        bpro::ThemeManager { theme_manager },
                        bpro::Text { "首页" },
                        bpro::Clickable { [this](auto&) {
                            page_stack_->setCurrentIndex(0);
                        }}
                    },

                    lnpro::Item<FilledButton> {
                        bpro::ThemeManager { theme_manager },
                        bpro::Text { "聊天" },
                        bpro::Clickable { [this](auto&) {
                            page_stack_->setCurrentIndex(1);
                        }}
                    },

                    lnpro::Item<FilledButton> {
                        bpro::ThemeManager { theme_manager },
                        bpro::Text { "课表" },
                        bpro::Clickable { [this](auto&) {
                            page_stack_->setCurrentIndex(2);
                        }}
                    },

                    lnpro::Item<FilledButton> {
                        bpro::ThemeManager { theme_manager },
                        bpro::Text { "校园卡" },
                        bpro::Clickable { [this](auto&) {
                            page_stack_->setCurrentIndex(3);
                        }}
                    },

                    lnpro::Item<FilledButton> {
                        bpro::ThemeManager { theme_manager },
                        bpro::Text { "请假" },
                        bpro::Clickable { [this](auto&) {
                            page_stack_->setCurrentIndex(4);
                        }}
                    },

                    lnpro::Item<FilledButton> {
                        bpro::ThemeManager { theme_manager },
                        bpro::Text { "通知" },
                        bpro::Clickable { [this](auto&) {
                            page_stack_->setCurrentIndex(5);
                        }}
                    },

                    lnpro::Item<FilledButton> {
                        bpro::ThemeManager { theme_manager },
                        bpro::Text { "审计" },
                        bpro::Clickable { [this](auto&) {
                            page_stack_->setCurrentIndex(6);
                        }}
                    },

                    lnpro::Stretch { 1 }
                }
            },

            lnpro::Item { page_stack_ }
        }
    };

    setCentralWidget(root);
    resize(1280, 800);

    theme_manager.apply_theme();
}
