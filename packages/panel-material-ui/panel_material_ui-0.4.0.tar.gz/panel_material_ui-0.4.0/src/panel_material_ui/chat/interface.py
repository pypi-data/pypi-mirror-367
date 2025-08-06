from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING

import param
from panel.chat.interface import CallbackState, ChatInterface
from panel.layout import Column, Row
from panel.pane.markup import Markdown

from .feed import ChatFeed
from .input import ChatAreaInput

if TYPE_CHECKING:
    pass

ICON_MAP = {
    "arrow-back": "undo",
    "trash": "delete",
}


class ChatInterface(ChatFeed, ChatInterface):
    """
    A chat interface that uses Material UI components.

    :References:

    - https://panel-material-ui.holoviz.org/reference/chat/ChatInterface.html
    - https://panel.holoviz.org/reference/chat/ChatInterface.html

    :Example:

    >>> ChatInterface().servable()
    """

    input_params = param.Dict(
        default={}, doc="Additional parameters to pass to the ChatAreaInput widget, like `enable_upload`."
    )

    _input_type = ChatAreaInput

    _rename = {"loading": "loading"}

    @param.depends("_callback_state", watch=True)
    async def _update_input_disabled(self):
        busy_states = (CallbackState.RUNNING, CallbackState.GENERATING)
        if not self.show_stop or self._callback_state not in busy_states or self._callback_future is None:
            self._widget.loading = False
        else:
            self._widget.loading = True

    @param.depends("widgets", "button_properties", watch=True)
    def _init_widgets(self):
        if len(self.widgets) > 1:
            raise ValueError("panel_material_ui.ChatInterface.widgets not supported.")
        self._init_button_data()
        actions = {}
        for name, data in self._button_data.items():
            if (
                name in ("send", "stop") or (name == "rerun" and not self.show_rerun) or
                (name == "undo" and not self.show_undo) or (name == "clear" and not self.show_clear)
            ):
                continue
            actions[name] = {'icon': ICON_MAP.get(data.icon, data.icon), 'callback': partial(data.callback, self), 'label': name.title()}
        self._widget = ChatAreaInput(actions=actions, sizing_mode="stretch_width", **self.input_params)
        self.link(self._widget, disabled="disabled_enter")
        callback = partial(self._button_data["send"].callback, instance=self)
        self._widget.param.watch(callback, "enter_pressed")
        self._widget.on_action("stop", self._click_stop)
        input_container = Row(self._widget, sizing_mode="stretch_width")
        self._input_container.objects = [input_container]
        self._input_layout = input_container

    def _click_send(
        self,
        event: param.parameterized.Event | None = None,
        instance: ChatInterface | None = None
    ) -> None:
        if self.disabled:
            return
        objects = []
        if self.active_widget.value:
            objects.append(Markdown(self.active_widget.value))
        objects.extend(self.active_widget.views)
        if not objects:
            return
        value = Column(*objects) if len(objects) > 1 else objects[0]
        self.send(value=value, user=self.user, avatar=self.avatar, respond=True)

    @param.depends("placeholder_text", "placeholder_params", watch=True, on_init=True)
    def _update_placeholder(self):
        self._placeholder = self._message_type(
            self.placeholder_text,
            avatar='PLACEHOLDER',
            css_classes=["message"],
            **self.placeholder_params
        )

__all__ = ["ChatInterface"]
