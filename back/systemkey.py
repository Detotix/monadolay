import xr
from time import sleep
from shared import shared
from ctypes import c_void_p, POINTER, byref
#import other.ctl
import subprocess

def main():
    extensions = ["XR_MND_headless"]
    app_info = xr.ApplicationInfo(
        application_name="monadolay_headless_instance",
        application_version=1,
        engine_name="overlay_engine",
        engine_version=1
    )

    create_info = xr.InstanceCreateInfo(
        application_info=app_info,
        enabled_extension_names=extensions
    )
    while True:
        try:
            instance = xr.create_instance(create_info)
            break
        except:
            sleep(10)

    system_id = xr.get_system(instance)


    session_info = xr.SessionCreateInfo(system_id=system_id)
    session = xr.create_session(instance, session_info)


    begin_info = xr.SessionBeginInfo(
        primary_view_configuration_type=xr.ViewConfigurationType.PRIMARY_STEREO
    )
    xr.begin_session(session, begin_info)

    action_set = xr.create_action_set(instance, xr.ActionSetCreateInfo(
        action_set_name="monadolay_vr_menu_buttons",
        localized_action_set_name="Menu Action Set",
        priority=0
    ))

    left_action = xr.create_action(action_set, xr.ActionCreateInfo(
        action_type=xr.ActionType.BOOLEAN_INPUT,
        action_name="left_menu_click",
        localized_action_name="Left Menu Click"
    ))

    right_action = xr.create_action(action_set, xr.ActionCreateInfo(
        action_type=xr.ActionType.BOOLEAN_INPUT,
        action_name="right_menu_click",
        localized_action_name="Right Menu Click"
    ))

    left_click_path = xr.string_to_path(instance, "/user/hand/left/input/system/click")
    right_click_path = xr.string_to_path(instance, "/user/hand/right/input/system/click")
    controller_profile_path = xr.string_to_path(instance, "/interaction_profiles/htc/vive_controller")

    bindings = [
        xr.ActionSuggestedBinding(action=left_action, binding=left_click_path),
        xr.ActionSuggestedBinding(action=right_action, binding=right_click_path)
    ]

    suggested = xr.InteractionProfileSuggestedBinding(
        interaction_profile=controller_profile_path,
        suggested_bindings=bindings
    )
    xr.suggest_interaction_profile_bindings(instance, suggested)

    attach_info = xr.SessionActionSetsAttachInfo(
        action_sets=[action_set]
    )
    xr.attach_session_action_sets(session, attach_info)




    sync_info = xr.ActionsSyncInfo(
        active_action_sets=[xr.ActiveActionSet(action_set=action_set)]
    )

    event_buf = xr.typedefs.EventDataBuffer()
    while True:
        sleep(0.05)
        #print(other.ctl.get_monado_instances())
        try:
            res = xr.raw_functions.xrPollEvent(instance, byref(event_buf))
            if res == xr.Result.EVENT_UNAVAILABLE:
                event = None
            else:
                event = event_buf
        except xr.exception.EventUnavailable:
            event = None
        if event is None:

            xr.sync_actions(session, sync_info)

            left_state = xr.get_action_state_boolean(session, xr.ActionStateGetInfo(action=left_action))
            right_state = xr.get_action_state_boolean(session, xr.ActionStateGetInfo(action=right_action))

            shared.systemkey_left=left_state.is_active and left_state.current_state
            shared.systemkey_right=right_state.is_active and right_state.current_state
        else:
            if event.type == xr.StructureType.EVENT_DATA_SESSION_STATE_CHANGED:
                state_event = xr.EventDataSessionStateChanged.from_buffer(event)
                if state_event.state in (xr.SessionState.EXITING, xr.SessionState.LOSS_PENDING):
                    break
if __name__=="__main__":
    main()