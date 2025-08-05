import struct
from ..defs import MouseButton, ControlMsgType,\
                   POINTER_ID_MOUSE, AKeyCode, AKeyEventAction, AMotionEventAction, AMotionEventButtons, ScreenPosition

class InjectKeyCode:
    msg_type: ControlMsgType = ControlMsgType.MSG_TYPE_INJECT_KEYCODE
    repeat: int = 0
    metastate: int = 0

    def __init__(self, key_code: AKeyCode, action: AKeyEventAction) -> None:
        self.key_code = key_code
        self.action = action

    def serialize(self) -> bytes:
        buf = struct.pack(
            ">BBIII",
            self.msg_type.value,
            self.action.value,
            self.key_code.value,
            self.repeat,
            self.metastate,
        )
        return buf

class InjectTouchEvent:
    msg_type: ControlMsgType = ControlMsgType.MSG_TYPE_INJECT_TOUCH_EVENT
    pointer_id = POINTER_ID_MOUSE

    def __init__(
        self,
        position: ScreenPosition,
        action: AMotionEventAction,
        buttons: AMotionEventButtons = AMotionEventButtons.AMOTION_EVENT_BUTTON_SECONDARY,
        action_button: AMotionEventButtons = AMotionEventButtons.AMOTION_EVENT_BUTTON_NONE,
    ) -> None:
        is_up = action == AMotionEventAction.AMOTION_EVENT_ACTION_UP
        self.pressure = 0 if is_up else 1
        self.position = position

        self.action = action
        self.buttons = buttons
        self.action_button = action_button

    def serialize(self) -> bytes:
        buf = struct.pack(
            ">BBQIIHHHII",
            self.msg_type.value, # 8
            self.action.value, # 8
            self.pointer_id, # 64
            self.position.point.x, # 32
            self.position.point.y, # 32
            self.position.size.width, # 16
            self.position.size.height, # 16
            self.pressure, # 16
            self.action_button, # 32
            self.buttons, # 32
        )
        return buf

def TouchMoveEvent(position: ScreenPosition) -> InjectTouchEvent:
    return InjectTouchEvent(
        position,
        AMotionEventAction.AMOTION_EVENT_ACTION_HOVER_MOVE,
    )
def TouchClickEvent(position: ScreenPosition, button: MouseButton, pressed: bool) -> InjectTouchEvent:
    abutton = AMotionEventButtons.AMOTION_EVENT_BUTTON_NONE
    match button:
        case MouseButton.left:
            abutton = AMotionEventButtons.AMOTION_EVENT_BUTTON_PRIMARY
        case MouseButton.right:
            abutton = AMotionEventButtons.AMOTION_EVENT_BUTTON_SECONDARY
        case MouseButton.middle:
            abutton = AMotionEventButtons.AMOTION_EVENT_BUTTON_TERTIARY

    action = None
    if pressed:
        action = AMotionEventAction.AMOTION_EVENT_ACTION_DOWN
    else:
        action = AMotionEventAction.AMOTION_EVENT_ACTION_UP

    return InjectTouchEvent(
        position,
        action,
        abutton,
        abutton,
    )