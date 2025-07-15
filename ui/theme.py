# -*- coding: utf-8 -*-

"""
이 모듈은 애플리케이션의 테마와 색상 팔레트를 관리합니다.
"""

# 라이트 테마 색상 팔레트
PALETTE_LIGHT = {
    "window_bg": "#f8fafc",
    "bg_element_white": "#ffffff",
    "bg_header": "#f1f5f9",
    "bg_tab": "#f1f5f9",
    "bg_tab_hover": "#e2e8f0",
    "bg_tab_selected": "#f8fafc",
    "bg_disabled": "#e2e8f0",
    "bg_progressbar": "#f1f5f9",
    "bg_scrollbar": "#f1f5f9",

    "text_primary": "#334155",
    "text_secondary": "#64748b",
    "text_title": "#0f172a",
    "text_header": "#64748b",
    "text_disabled": "#94a3b8",
    "text_button": "#ffffff",
    "text_button_warning": "#422006",
    "text_selection": "#ffffff",
    "text_progressbar": "#334155",
    "text_error": "#ef4444",

    "border_default": "#cbd5e1",
    "border_subtle": "#94a3b8",
    "border_light": "#e2e8f0",
    "border_disabled": "#e2e8f0",
    "border_focus": "#3b82f6",
    "border_radio_checked": "#3b82f6",

    "interactive_primary": "#3b82f6",
    "interactive_primary_hover": "#2563eb",
    "interactive_primary_pressed": "#1d4ed8",
    "interactive_secondary": "#e2e8f0",
    "interactive_secondary_hover": "#cbd5e1",
    "interactive_secondary_pressed": "#94a3b8",
    "interactive_success": "#22c55e",
    "interactive_success_hover": "#16a34a",
    "interactive_success_pressed": "#15803d",
    "interactive_danger": "#ef4444",
    "interactive_danger_hover": "#dc2626",
    "interactive_danger_pressed": "#b91c1c",
    "interactive_warning": "#eab308",
    "interactive_warning_hover": "#ca8a04",
    "interactive_warning_pressed": "#a16207",

    "checkbox_checked_bg": "#3b82f6",
    "checkbox_checked_border": "#3b82f6",
    
    "slider_groove": "#e2e8f0",
    "slider_handle_border": "#ffffff",
    "scrollbar_handle": "#cbd5e1",
    "scrollbar_handle_hover": "#94a3b8",

    "icon_combo_arrow": "url(:/icons/down_arrow.png)",
    "icon_checkbox_check": "url(:/icons/check.png)",
    "icon_up_arrow": "url(:/icons/up_arrow.png)",
    "icon_left_arrow": "url(:/icons/left_arrow.png)",
    "icon_right_arrow": "url(:/icons/right_arrow.png)",
    "icon_radio_dot": "url(:/icons/radio_dot.png)",
}

# 다크 테마 색상 팔레트
PALETTE_DARK = {
    "window_bg": "#0f172a",
    "bg_element_white": "#1e293b", # Actually slate-800
    "bg_header": "#0f172a",
    "bg_tab": "#1e293b",
    "bg_tab_hover": "#334155",
    "bg_tab_selected": "#0f172a",
    "bg_disabled": "#334155",
    "bg_progressbar": "#334155",
    "bg_scrollbar": "#1e293b",

    "text_primary": "#e2e8f0",
    "text_secondary": "#94a3b8",
    "text_title": "#e2e8f0",
    "text_header": "#94a3b8",
    "text_disabled": "#94a3b8",
    "text_button": "#ffffff",
    "text_button_warning": "#422006",
    "text_selection": "#ffffff",
    "text_progressbar": "#e2e8f0",
    "text_error": "#ef4444",

    "border_default": "#475569",
    "border_subtle": "#94a3b8",
    "border_light": "#334155",
    "border_disabled": "#475569",
    "border_focus": "#3b82f6",
    "border_radio_checked": "#3b82f6",

    "interactive_primary": "#3b82f6",
    "interactive_primary_hover": "#2563eb",
    "interactive_primary_pressed": "#1d4ed8",
    "interactive_secondary": "#334155",
    "interactive_secondary_hover": "#475569",
    "interactive_secondary_pressed": "#64748b",
    "interactive_success": "#22c55e",
    "interactive_success_hover": "#16a34a",
    "interactive_success_pressed": "#15803d",
    "interactive_danger": "#ef4444",
    "interactive_danger_hover": "#dc2626",
    "interactive_danger_pressed": "#b91c1c",
    "interactive_warning": "#eab308",
    "interactive_warning_hover": "#ca8a04",
    "interactive_warning_pressed": "#a16207",

    "checkbox_checked_bg": "#3b82f6",
    "checkbox_checked_border": "#3b82f6",

    "slider_groove": "#334155",
    "slider_handle_border": "#0f172a",
    "scrollbar_handle": "#475569",
    "scrollbar_handle_hover": "#64748b",

    "icon_combo_arrow": "url(:/icons/down_arrow_dark.png)",
    "icon_checkbox_check": "url(:/icons/check.png)",
    "icon_up_arrow": "url(:/icons/up_arrow.png)",
    "icon_left_arrow": "url(:/icons/left_arrow.png)",
    "icon_right_arrow": "url(:/icons/right_arrow.png)",
    "icon_radio_dot": "url(:/icons/radio_dot.png)",
}