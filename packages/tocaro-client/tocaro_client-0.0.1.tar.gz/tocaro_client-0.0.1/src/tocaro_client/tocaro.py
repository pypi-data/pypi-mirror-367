from __future__ import annotations

import json
import logging
import threading
import time
from dataclasses import asdict, dataclass, field, is_dataclass
from enum import Enum, auto
from typing import Callable, Optional

from dataclasses_json import LetterCase, dataclass_json

import requests
from requests import Response

logging.getLogger().setLevel(logging.INFO)
_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.INFO)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# add the handler to the root logger
_LOGGER.addHandler(console)


def threaded(fn):
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=fn, args=args, kwargs=kwargs)
        thread.start()
        return thread

    return wrapper


class ToCaroError(Exception):
    """A generic ToCaro Error"""

    pass


class ToCaroConflictError(ToCaroError):
    """
    There was a conflict (for example if the resource already existed, or the validation failed)
    """

    pass


class ToCaroNotFoundError(ToCaroError):
    """
    The resource was not found
    """

    pass


class ToCaroAuthInvalid(ToCaroError):
    """
    The provided credentials are not correct
    """

    def __init__(self):
        super().__init__("The provided credentials are not correct")

    pass


class ToCaroRequestFailed(ToCaroError):
    """
    The request failed
    """

    def __init__(self, response: Response):
        self.response = response
        super().__init__(
            f"The request failed! ({response.status_code}) - {response.reason} - {response.text}"
        )

    pass


class ToCaroForbidden(ToCaroError):
    """
    The credentials are not valid for this request
    """

    def __init__(self):
        super().__init__("The provided credentials are not suitable for this request")

    pass


class _EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if is_dataclass(o):
            return asdict(o)
        return super().default(o)


class ToCaroEvent(Enum):
    """
    Event Enums for ToCaro

    Notes
    -----
    If you use subscribe to these events please make sure the function has the correct keyword parameters!
    """

    stopped = auto()
    """
        will be triggered once if the stop method was called

        Parameter
        ---------
            ToCaro: ToCaroClient
                The ToCaro client
        """

    message_received = auto()
    """
        Parameter
        ---------

            ToCaro: ToCaroClient
                The ToCaro client
            sender: str
                The device that sent the message
            receiver: str
                The device that received the message
            payload: Object
                The payload of the message
    """

    config_updated = auto()
    """
        Parameter
        ---------

            ToCaro: ToCaroClient
                The ToCaro client
            device: str
                The device that was updated
            config: Object
                The payload of the message
    """
    init_done = auto()
    """
        will be triggered once the connection is fully established and the initial sync was done

        Parameter
        ---------
            ToCaro : ToCaroClient
                The ToCaro client
        """


@dataclass_json(
    letter_case=LetterCase.CAMEL
)  # This converts snakeCase variables to camel_case variables
@dataclass
class ToCaroAction:
    """
    A ToCaro Action
    """

    user_id: str
    emotion: ToCaroEmotion
    maximum_intensity: float
    minimum_intensity: float
    actions: list[ToCaroActionItem]


@dataclass_json(
    letter_case=LetterCase.CAMEL
)  # This converts snakeCase variables to camel_case variables
@dataclass
class ToCaroActionItem:
    device_id: str
    type: "ToCaroActionType"
    data: dict[str, str | int | float | bool | None] = field(default_factory=dict)


@dataclass_json(
    letter_case=LetterCase.CAMEL
)  # This converts snakeCase variables to camel_case variables
@dataclass
class ToCaroConfiguration:
    """ """

    id: str
    name: str


@dataclass_json(
    letter_case=LetterCase.CAMEL
)  # This converts snakeCase variables to camel_case variables
@dataclass
class ToCaroDevice:
    """
    A ToCaro Device
    """

    id: str
    name: str
    is_active: bool

    def __str__(self):
        return f"ToCaro Device {self.id}({self.name}) {self.status.value}"


class ToCaroDeviceStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class ToCaroEmotion(str, Enum):
    ANGER = "anger"
    FEAR = "fear"
    ENJOYMENT = "enjoyment"
    SADNESS = "sadness"
    DISGUST = "disgust"


class ToCaroActionType(str, Enum):
    LIGHT_STATIC = "lightStatic"
    LIGHT_DYNAMIC = "lightDynamic"
    LIGHT_PULSE = "lightPulse"
    LIGHT_WAVE = "lightWave"
    VIBRATE = "vibrate"
    SOUND = "sound"
    HEART_BEAT = "heartBeat"
    TEMPERATURE = "temperature"


@dataclass_json
@dataclass
class ToCaroUser:
    id: int
    name: str


class ToCaroClient:
    """
    The baseclass for our ToCaro Client
    """

    def __init__(
        self,
        base: str,
        username: str,
        password: str,
        client_id: str,
        client_secret: str,
        subs: Optional[dict[ToCaroEvent, Callable]] = None,
        debug=False,
        login_server: Optional[str] = None,
        message_delay=5,
        config_delay=60,
        device: Optional[str] = None,
    ):
        """
        Creates a new instance of the ToCaro Client

        Parameters
        ----------
        base : str
            The base for the server
        username : str
            The username to use
        password : str
            The password to use
        subs: dict[ToCaroEvent,Callable]
            The subscriptions to start with
        login_server: Optional[str]
            The login server to use, if not given the base will be used
        client_id: str
            The client id to use
        client_secret: str
            The client secret to use
        debug: bool
            If True, debug messages will be printed
        message_delay: int
            The delay in seconds between two polls for new messages
        config_delay: int
            The delay in seconds between two polls for new configurations
        device: Optional[str]
            The device to use, if not given the first device will be used

        Examples
        --------

        sync without async updates
        >>> ToCaro = ToCaroClient("http://localhost:18080", "user", "pass")



        async with listeners
        >>> with ToCaroClient("http://localhost:18080", "user", "pass",
        >>>               subs={
        >>>                   ToCaroEvent.auth_ok: on_auth_ok,
        >>>                   ToCaroEvent.device_created: on_device_created,
        >>>                   ToCaroEvent.device_attribute_updated: on_device_attribute_changed
        >>>               }) as ToCaro:

        """
        self.__message_delay = message_delay
        self.__config_delay = config_delay
        self.__stopped = False
        self.__subscribers: dict[ToCaroEvent, list[Callable]] = {}
        if client_id is not None:
            self.__client_id = client_id
        else:
            self.__client_id = "python-tocaro-client"
        if client_secret is not None:
            self.__client_secret = client_secret
        else:
            self.__client_secret = "your_client_secret"
        self.__token: Optional[dict] = None
        if subs is not None:
            for i, (event_type, fn) in enumerate(subs.items()):
                self.subscribe(event_type, fn)
        self.__base = base
        if login_server is not None:
            self.__login_server = login_server
        else:
            self.__login_server = base
        self.__username = username
        self.__password = password
        self.__debug = debug
        self.__device = device
        self.__configs: dict[str, dict] = {}
        self.__devices: list[ToCaroDevice] = []
        self.__last_id: dict[str, str] = {}
        self.__known_messages: dict[str, list[str]] = {}
        self.get_devices()

    def _get_devices(self) -> list[ToCaroDevice]:
        """
        Get the list of devices we have access to

        This will return the devices that are available to this client.
        If no devices are available, it will return an empty list.

        Returns
        -------
        list[ToCaroDevice]
            The list of devices that are available to this client.
        """
        return self.__devices

    def _get_config(self, deviceId: Optional[str] = None) -> dict | None:
        """
        Get the configuration for a device

        This will return the configuration for the given device.
        If no deviceId is given, it will return the configuration for the first device.
        If no devices are available, it will return None.

        Parameters
        ----------
        deviceId : Optional[str], optional
            UUID of the device to get the config for, by default None

        Returns
        -------
        dict | None
            Either the configuration for the given device or None if no device is available or the device does not exist.
        """

        if deviceId is None:
            if len(self.__devices) == 0:
                self.get_devices()
            if len(self.__devices) > 0:
                deviceId = self.__devices[0].id
        if deviceId is not None:
            if deviceId not in self.__configs:

                self.__configs[deviceId] = self.get_config(deviceId=deviceId)

            if deviceId in self.__configs:
                return self.__configs[deviceId]
        return None

    def get_configs(self):
        """
        Updates the configuration for all devices

        This will fetch the configuration for all devices we have access to.
        If the configuration for a device has changed, it will trigger the config_updated event.
        """
        for d in self.__devices:
            old_c = None
            if d.id in self.__configs:
                old_c = self.__configs[d.id]
            c = self.get_config(d.id)
            if c != old_c:
                self.__post_event(
                    event_type=ToCaroEvent.config_updated,
                    data={"device": d.id, "config": c},
                )
                self.__configs[d.id] = c

    def __enter__(self) -> "ToCaroClient":
        """
        This will be called when the client is used in a with statement.

        It will start the polling for events and configurations and return the client itself.

        Returns
        -------
        ToCaroClient
            The client itself, so you can use it in the with statement
        """

        self.poll_config()
        self.poll_events()
        return self

    def __post_event(self, event_type: ToCaroEvent, data):
        if self.__debug:
            _LOGGER.info(f"publishing {event_type} with data:{data}")
        if event_type not in self.__subscribers:
            return
        for fn in self.__subscribers[event_type]:
            fn(self, **data)

    def __exit__(self, type, value, traceback):
        self.stop()

    def get_config(self, deviceId: str, wanted_status=200) -> dict:
        return self.__do_request(
            "GET",
            "/api/ToCaro/Configuration",
            params={"deviceId": deviceId},
            wanted_status=wanted_status,
        ).json()

    def post_config(self, deviceId: str, payload: str, wanted_status=200):
        """
        Post a device configuration to the ToCaro Server

        This will update the configuration of the device with the given id.
        If the device does not exist, it will be created.

        Parameters
        ----------
        deviceId : str
            UUID of the device to update
        payload : str
            The configuration to set, as a stringified json or a dict
        wanted_status : int, optional
            The status we assume to have, by default 200
        """
        configstr = None
        if isinstance(payload, str):
            configstr = payload
        elif isinstance(payload, dict) or isinstance(payload, dict):
            configstr = json.dumps(payload)
        else:
            _LOGGER.error(f"could not understand config type of {type(payload)}")
            return
        if configstr is not None:
            self.__do_request(
                "POST",
                "/api/ToCaro/Configuration",
                body={"deviceId": deviceId, "configurationJson": configstr},
                wanted_status=wanted_status,
            )

    def post_event(self, receiver: str, sender: str, payload: str, wanted_status=200):
        """
        Post an event to the ToCaro Server

        This will send an event from the sender to the receiver.
        The payload can be a stringified json or a dict.

        Parameters
        ----------
        receiver : str
            The UUID of the device that should receive the event
        sender : str
            The UUID of the device that sent the event
        payload : str
            The payload of the event, as a stringified json or a dict
        wanted_status : int, optional
            The status we assume to have, by default 200
        """
        eventpayload = None
        if isinstance(payload, str):
            eventpayload = payload
        elif isinstance(payload, dict) or isinstance(payload, dict):
            eventpayload = json.dumps(payload)
        else:
            print(f"could not understand config type of {type(payload)}")
        if eventpayload is not None:
            self.__do_request(
                "POST",
                "/api/ToCaro/Message",
                body={
                    "senderDeviceId": sender,
                    "receiverDeviceId": receiver,
                    "payloadJson": eventpayload,
                },
                wanted_status=wanted_status,
            )

    def get_events(
        self, deviceId: str, lastEvent: Optional[str] = None, wanted_status=200
    ) -> list[dict]:
        """
        Get the events for a device

        This will return the events for the given device.
        If lastEvent is given, it will only return events that are newer than the lastEvent.

        Parameters
        ----------
        deviceId : str
            UUID of the device to get events for
        lastEvent : Optional[str], optional
            The ID of the last event we received, if given only events newer than this will be returned,
            defaults to None
        wanted_status : int, optional
            The status we assume to have, by default 200
        Returns
        -------
        list[dict]
            A list of events for the given device
        """

        params = {"deviceId": deviceId}
        if lastEvent is not None:
            params["lastEvent"] = lastEvent
        return self.__do_request(
            "GET",
            "/api/ToCaro/Messages",
            params=params,
            wanted_status=wanted_status,
        ).json()

    def get_pairs(self, wanted_status=200) -> list[tuple[str, str]]:
        """
        Get the pairs from the ToCaro Server

        This will return the pairs of devices that are connected to each other.
        A pair is a tuple of two device IDs.

        Parameters
        ----------
        wanted_status : int, optional
            The status we assume to have, by default 200

        Returns
        -------
        list[tuple[str, str]]
            A list of pairs of device IDs that are connected to each other.
        """
        return self.__do_request(
            "GET",
            "/api/ToCaro/Pair",
            wanted_status=wanted_status,
        ).json()

    def get_devices(self):
        """
        Get the devices from the ToCaro Server
        """
        data = self.__do_request("GET", "/api/ToCaro/Device", wanted_status=200)
        # print(data.json())
        self.__devices = []
        # self.devices = dataclasses_json.loads(data.text, ToCaroDevice, many=True)
        for dd in data.json():
            dev = ToCaroDevice.from_dict(dd)
            self.__devices.append(dev)

    def pull_events(self):
        """
        This pulls the events from the ToCaro Server, for all events that are owned by this user.
        """
        for device in self.__devices:
            if device.is_active:
                if device.id not in self.__known_messages:
                    self.__known_messages[device.id] = []
                if device.id in self.__last_id:
                    lastId = self.__last_id[device.id]
                else:
                    lastId = None
                data = self.get_events(deviceId=device.id, lastEvent=lastId)
                # print(data)
                if len(data) > 0:
                    for d in data:
                        if d in self.__known_messages[device.id]:
                            continue
                        self.__known_messages[device.id].append(d)

                        try:
                            if isinstance(d["payloadJson"], str):
                                payload = json.loads(d["payloadJson"])
                            elif isinstance(d["payloadJson"], dict) or isinstance(
                                d["payloadJson"], list
                            ):
                                payload = d["payloadJson"]
                            else:
                                print(
                                    f"error could not understand type {type(d['payloadJson'])}"
                                )
                                continue

                            self.__last_id[device.id] = d["id"]
                            self.__post_event(
                                event_type=ToCaroEvent.message_received,
                                data={
                                    "sender": d["senderDeviceId"],
                                    "receiver": device.id,
                                    "payload": payload,
                                },
                            )

                        except (json.JSONDecodeError, TypeError) as e:
                            print("error ", e)
                            pass
                    pass
        # self.__post_event(event_type=ToCaroEvent.init_done, data={})

    @threaded
    def poll_config(self):
        """
        This polls the configuration from the ToCaro Server for all devices, will be run in a separate thread and will update the configuration
        every config_delay seconds.
        """
        while not self.__stopped:
            self.get_configs()
            if self.__stopped:
                break
            time.sleep(self.__config_delay)

    @threaded
    def poll_events(self):
        """
        This polls the events from the ToCaro Server for all devices, will be run in a separate thread and will update the events every
        message_delay seconds.
        """
        while not self.__stopped:
            self.update()
            if self.__stopped:
                break
            time.sleep(self.__message_delay)

    def subscribe(self, event_type: ToCaroEvent, fn: Callable) -> None:
        """
        subscribe to an event with the given Callable

        Parameters
        ----------
        event_type : ToCaroEvent
            The event type to listen to
        fn : Callable
            The function that fulfills the keyword parameters seen in the documentation for each ToCaroEvent
        Examples
        --------

        Subscribe to auth events
        >>> def on_auth_ok(ToCaro: ToCaroClient):
        >>>     print(f"auth okay  on {ToCaro}...")
        >>> ToCaro.subscribe(ToCaroEvent.auth_ok, on_auth_ok)


        Subscribe to changed attributes
        >>> def on_device_attribute_changed(ToCaro: ToCaroClient, device: ToCaroDevice,
        >>>     attribute: str | int | float, value: str | int | bool | float | list | tuple | None | dict):
        >>>     print(f"change on {ToCaro} {device} - set {attribute} to {value}")
        >>> ToCaro.subscribe(ToCaroEvent.device_attribute_updated, on_device_attribute_changed)


        """
        if event_type not in self.__subscribers:
            self.__subscribers[event_type] = []
        self.__subscribers[event_type].append(fn)

    def is_stopped(self) -> bool:
        """
        check if the client got the command to stop itself

        Returns
        -------
        bool:
        True if the client should be stopping
        """
        return self.__stopped

    def stop(self) -> None:
        """
        Signal the client that we would want to stop the client.
        Will close all connections
        """
        self.__stopped = True
        self.__post_event(ToCaroEvent.stopped, {})

    def login(self):
        """
        Try to login

        Parameters
        ----------

        Returns
        -------
        True if login succeeded

        Raises
        -------
        ToCaroAuthInvalid
            The auth was invalid
        ToCaroError
            Anything else went wrong
        """
        return self.__refresh_token()

    def __refresh_token(self) -> bool:
        r = requests.post(
            f"{self.__login_server}/connect/token",
            data={
                "client_id": self.__client_id,
                "client_secret": self.__client_secret,
                "username": self.__username,
                "password": self.__password,
                "grant_type": "password",
                "scope": "api.b2c",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if r.status_code == 200:
            # _LOGGER.info(f"logged in with token:{r.text}")

            self.__token = r.json()
            return True
        else:
            _LOGGER.error(f"login FAILED {r.status_code} {r.json()}")
            self.__token = None
        return False

    def __do_request(
        self,
        method: str,
        url: str,
        params: Optional[dict] = None,
        body: str | dict | None = None,
        tries_left: int = 1,
        wanted_status: Optional[int] = None,
    ) -> Response:
        """
        send a request to ToCaro

        Parameters
        ----------
        method: str
            The HTTP-Method to use (POST,GET,DELETE,OPTIONS,PUT)
        url: str
            The url to use - if its not a fully qualified url it will be prefixed with the base url
        params: dict
            A dict with the parameters, defaults to None

        body: str
            The body to send with a post or put, defaults to None
        tries_left: int
            The number of tries we want to try it for, defaults to 1

        wanted_status: int
            the HTTP Status Code we expect, if plausible the request will be tried again if the actual HTTP Status Code differs

        Raises
        -------
        ToCaroRequestFailed
            The request failed for some reason (most likely its return code was not equal to wanted_status
        ToCaroAuthInvalid
            The auth was returned as invalid
        ToCaroForbidden
            The auth has no access to this
        ToCaroError
            Some error occured


        """

        if self.__token is None:
            self.__refresh_token()
        if not url.startswith("http://") and not url.startswith("https://"):
            if url.startswith("/"):
                url = f"{self.__base}{url}"
            else:
                url = f"{self.__base}/{url}"

        if self.__token is not None:
            headers = {"authorization": f"Bearer {self.__token['access_token']}"}
            if isinstance(body, dict) or isinstance(body, list):
                # convert to stringified json
                body = json.dumps(body, default=str)
                # headers.update("Content-Type":"application/json")
                headers["Content-Type"] = "application/json"
            # add header
            r = requests.request(
                method=method, url=url, params=params, headers=headers, data=body
            )
            # _LOGGER.info(f"got result {r.status_code} for {url} - tries left {tries_left}")
            if wanted_status is not None and r.status_code == wanted_status:
                return r
            if r.status_code == 409:
                # we cannot fix 409, dont try again  if its already there it is already there
                raise ToCaroConflictError(f"{r.reason} {r.text}")
            if r.status_code == 404:
                # we cannot fix 404, dont try again
                raise ToCaroNotFoundError(f"{r.reason} {r.text}")
            if r.status_code == 403:
                # we cannot fix 403, dont try again
                raise ToCaroForbidden()
            if tries_left > 0:
                # check if we would be allowed to try again
                if r.status_code == 401:
                    # 401 can be saved, reset the token first
                    self.__token = None
                    return self.__do_request(
                        method, url, params, body, tries_left - 1, wanted_status
                    )
                if wanted_status is not None and r.status_code != wanted_status:
                    # the status was not what we wanted and might be fixable
                    return self.__do_request(
                        method, url, params, body, tries_left - 1, wanted_status
                    )
            if r.status_code == 401:
                raise ToCaroAuthInvalid()

            raise ToCaroRequestFailed(r)
        raise ToCaroAuthInvalid()

    def __str__(self):
        return f"ToCaro Client ({self.__username})"
