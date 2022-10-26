from kivy.factory import Factory

from kivy.app import App
from kivy.lang import Builder

Builder.load_string("""
#: import icon tools.icon_def.x_icons
#: import win kivy.core.window.Window
#: import get_color_from_hex kivy.utils.get_color_from_hex
#: import ScrollEffect kivy.effects.scroll.ScrollEffect
<IconButton@HoverBehavior+ButtonBehavior+Label>:
    icon: ""
    text: icon[self.icon] if self.icon else ""
    size_hint: None, None
    size: self.texture_size
    font_name: "Icon"
    padding: dp(5), dp(5)
    pos_hint: {"center_y": .5}
    on_leave: self.color = 1, 1, 1, 1

<Input@HoverBehavior+TextInput>:
    background_normal: ""
    background_active: ""
    background_disabled_normal: ""
    background_color: 0, 0, 0, .5
    foreground_color: get_color_from_hex("#00C853")
    disabled_foreground_color: self.foreground_color
    size_hint: None, None
    font_name: "Ubuntu"
    size: dp(200), dp(30)
    on_enter: win.set_system_cursor("ibeam")
    on_leave: win.set_system_cursor("arrow")

<Log@Label>:
    text_size: self.width, None
    color: get_color_from_hex("#00C853")
    bold: True
    font_name: "Ubuntu"

<ButtonLabel@ButtonBehavior+Label>:
    size_hint: None, None
    size: self.texture_size
    bold: True
    padding: dp(50), dp(10)
    bg_color: 0, 0, 0, .5
    line_color: 0, 0, 0, 0
    radius: [dp(0)]
    canvas.before:
        Color:
            rgba: self.bg_color
        RoundedRectangle:
            size: self.size
            pos: self.pos
            radius: self.radius or [dp(0)]
        Color:
            rgba: self.line_color
        Line:
            points: self.x, self.y, self.width, self.y

<BlackBox@RecycleView>:
    effect_cls: ScrollEffect
    viewclass: "Log"
    canvas.before:
        Color:
            rgba: 0, 0, 0, .7
        RoundedRectangle:
            size: self.size
            pos: self.pos
            radius: [dp(20)]
    RecycleBoxLayout:
        orientation: "vertical"
        size_hint_y: None
        height: self.minimum_height
        spacing: dp(5)
        default_size_hint: 1, None
        padding: dp(10)
        # magic value for the default height of the message
        default_size: 0, dp(30)

<ProtocolBox@BoxLayout>:
    orientation: "vertical"
    spacing: dp(10)
    size_hint: None, None
    size: self.minimum_size
    pos_hint: {"center_x": .5}
    Label:
        text: "SERVER IP ADDRESS"
        size_hint: None, None
        size: self.texture_size   
    ButtonLabel:
        id: ip
        text: "0.0.0.0"
        size: dp(200), self.texture_size[1]
        color: get_color_from_hex("#00C853")
        radius: [dp(5), dp(5), 0, 0]
        padding_x: dp(10)
        disabled_outline_color: self.color
        disabled_color: self.color
        on_release: app.open_dropdown(args[0])
    Label:
        text: "PORT"
        size_hint: None, None
        size: self.texture_size   
    Input:
        id: port
        text: "5567"
        input_type: "number"
        input_filter: "int"
    Label:
        text: "SELECT FOLDER"
        size_hint: None, None
        size: self.texture_size
    ButtonLabel:
        id: folder_name
        text: app.resolve_cache_path or "open filechooser"
        padding_x: dp(10)
        size: dp(200), self.texture_size[1]
        color: get_color_from_hex("#00C853")
        radius: [dp(5), dp(5), 0, 0]
        disabled_outline_color: self.color
        disabled_color: self.color
        text_size: self.width, None
        shorten: True
        shorten_from: "left"
        on_release: app.choose_write_location(self)


<TitleBar@BoxLayout>:
    size_hint_y: None
    height: self.minimum_height
    padding: dp(2)
    spacing: dp(15)
    IconButton:
        id: icon
        icon: "computer-tower-f"
        color: get_color_from_hex("#C51162")
        font_size: "20sp"
    Label:
        text: "Fleet"
        size_hint_y: None
        height: self.texture_size[1]
        text_size: self.size
        bold: True
        pos_hint: {"center_y": .5}
    IconButton:
        draggable: False
        icon: "minus-l"
        on_release: win.minimize()
        on_enter: self.color = get_color_from_hex("#00C853")
    IconButton:
        icon: "square-l"
        draggable: False
        maximize: True
        on_enter: self.color = get_color_from_hex("#00C853")
        on_release:
            self.icon = "square-l" if self.icon == "cards-l" else "cards-l"
            win.maximize() if self.maximize else win.restore()
            self.maximize = not self.maximize
    IconButton:
        draggable: False
        icon: "x-l"
        on_enter: self.color = "red"
        on_release:
""", filename="main.kv", rulesonly=True)
title_bar = Factory.TitleBar()
