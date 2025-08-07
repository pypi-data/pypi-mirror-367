import os
import random
import secrets
import uuid
from dataclasses import dataclass

from dataclasses_json import dataclass_json

import pytest

from random_dict import (
    random_bool,
    random_dict,
    random_float,
    random_int,
    random_string,
)

import requests
from requests.exceptions import ConnectionError

try:
    from tocaro_client.tocaro import (
        ToCaroAuthInvalid,
        ToCaroClient,
        ToCaroDeviceStatus,
        ToCaroForbidden,
    )
except ModuleNotFoundError:
    import sys

    sys.path.append(os.path.abspath("src"))
    print(sys.path)
    from tocaro_client.tocaro import (
        ToCaroAuthInvalid,
        ToCaroClient,
        ToCaroDeviceStatus,
        ToCaroForbidden,
    )

import yaml


@dataclass_json
@dataclass
class Device:
    id: str
    owner: str
    name: str
    status: ToCaroDeviceStatus


@dataclass_json
@dataclass
class User:
    email: str
    password: str
    devices: list[Device]


NUM_PAIRS = 2
NUM_USERS = NUM_PAIRS * 2
NUM_DEVICES_PER_USER = 2
NUM_CLIENTS = 2
# devices = []
config = {"users": [], "clients": [], "devices": [], "pairs": []}
users = []
for i in range(1, NUM_USERS + 1):
    devices = []
    for j in range(1, NUM_DEVICES_PER_USER + 1):
        devices.append(
            {
                "name": f"ToCaro{i:0>2}_{j:0>2}",
                "owner": f"tocaro{i:0>2}@foo.bar",
                "id": str(uuid.uuid4()),
                "status": "ACTIVE",
            }
        )

    users.append(
        User.from_dict(
            {
                "email": f"tocaro{i:0>2}@foo.bar",
                "password": secrets.token_hex(16),
                "devices": devices,
            }
        )
    )

for p in range(0, NUM_PAIRS):

    user1 = users[p * 2]
    user2 = users[p * 2 + 1]
    config["pairs"].append([user1.devices[0].id, user2.devices[0].id])
    config["pairs"].append([user2.devices[0].id, user1.devices[0].id])
for u in users:
    config["users"].append({"email": u.email, "password": u.password})
    for d in u.devices:
        config["devices"].append(
            {
                "name": d.name,
                "owner": u.email,
                "id": d.id,
                "status": str(d.status.value),
            }
        )

for i in range(NUM_CLIENTS):
    config["clients"].append(
        {"client_secret": secrets.token_hex(32), "client_id": secrets.token_hex(32)}
    )


def random_client():
    return random.choice(config["clients"])


def is_responsive(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return True
    except ConnectionError:
        return False


def random_payload():
    return random_dict(
        max_depth=4,
        max_height=3,
        key_generators=[random_string],
        value_generators=[random_string, random_int, random_float, random_bool],
    )


@pytest.fixture(scope="session")
def http_service(docker_ip, docker_services):
    """Ensure that HTTP service is up and responsive."""

    # `port_for` takes a container port and returns the corresponding host port
    port = docker_services.port_for("mock-server", 5000)
    url = "http://{}:{}".format(docker_ip, port)
    docker_services.wait_until_responsive(
        timeout=30.0, pause=0.1, check=lambda: is_responsive(url)
    )
    return url


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    return os.path.join(str(pytestconfig.rootdir), "mock-compose.yaml")


def test_alive(http_service):
    status = 200
    response = requests.get(http_service + "/health-check")

    assert response.status_code == status


# Pin the project name to avoid creating multiple stacks
@pytest.fixture(scope="session")
def docker_compose_project_name() -> str:
    return "tocaro-python-test"


# Stop the stack before starting a new one
@pytest.fixture(scope="session")
def docker_setup():

    with open("config.yaml", "w") as outfile:
        yaml.dump(config, outfile, default_flow_style=False)

    return ["down -v", "up --build -d"]


@pytest.mark.run(after="test_alive")
def test_fake_logins(http_service):
    with pytest.raises(ToCaroAuthInvalid):
        client = random_client()
        ToCaroClient(
            base=http_service,
            username=str(uuid.uuid4()),
            password=users[0].password,
            client_id=client["client_id"],
            client_secret=client["client_secret"],
        )
        pytest.fail("should not have been able to log in with random username")

    with pytest.raises(ToCaroAuthInvalid):
        client = random_client()
        ToCaroClient(
            base=http_service,
            username=users[0].email,
            password="",
            client_id=client["client_id"],
            client_secret=client["client_secret"],
        )
        pytest.fail("should not have been able to log in without password")
    with pytest.raises(ToCaroAuthInvalid):
        client = random_client()
        ToCaroClient(
            base=http_service,
            username="",
            password=users[0].password,
            client_id=client["client_id"],
            client_secret=client["client_secret"],
        )
        pytest.fail("should not have been able to log in without username")
    with pytest.raises(ToCaroAuthInvalid):
        client = random_client()
        ToCaroClient(
            base=http_service,
            username=users[0].email,
            password=users[1].password,
            client_id=client["client_id"],
            client_secret=client["client_secret"],
        )
        pytest.fail("should not have been able to log in with wrong password")


@pytest.mark.run(after="test_alive")
def test_login(http_service):

    for i in range(0, NUM_USERS):
        client = random_client()
        users[i].client = ToCaroClient(
            base=http_service,
            username=users[i].email,
            password=users[i].password,
            client_id=client["client_id"],
            client_secret=client["client_secret"],
        )
        assert len(users[i].client._get_devices()) == NUM_DEVICES_PER_USER


@pytest.mark.run(after="test_login")
def test_fake_clients(http_service):
    with pytest.raises(ToCaroAuthInvalid):
        client = random_client()

        ToCaroClient(
            base=http_service,
            username=users[0].email,
            password=users[0].password,
            client_id="",
            client_secret=client["client_secret"],
        )
        pytest.fail("should not have been able to log in without client_id")

    with pytest.raises(ToCaroAuthInvalid):
        client = random_client()
        ToCaroClient(
            base=http_service,
            username=users[0].email,
            password=users[0].password,
            client_id=client["client_id"],
            client_secret="",
        )
        pytest.fail("should not have been able to log in without client_secret")

    with pytest.raises(ToCaroAuthInvalid):
        client = random_client()
        ToCaroClient(
            base=http_service,
            username=users[0].email,
            password=users[1].password,
            client_id=str(uuid.uuid4()),
            client_secret=client["client_secret"],
        )
        pytest.fail("should not have been able to log in with fake client id")

    with pytest.raises(ToCaroAuthInvalid):
        client = random_client()
        ToCaroClient(
            base=http_service,
            username=users[0].email,
            password=users[1].password,
            client_id=client["client_id"],
            client_secret=str(uuid.uuid4()),
        )
        pytest.fail("should not have been able to log in fake client secret")

    with pytest.raises(ToCaroAuthInvalid):
        ToCaroClient(
            base=http_service,
            username=users[0].email,
            password=users[1].password,
            client_id=str(uuid.uuid4()),
            client_secret=str(uuid.uuid4()),
        )
        pytest.fail("should not have been able to log in fake client data")


@pytest.mark.run(after="test_login")
def test_pairs(http_service):
    assert NUM_USERS > 0, "NUM_USERS should be larger than 0"
    for i in range(0, NUM_USERS):
        pairs = users[i].client.get_pairs()
        assert len(pairs) == 1
        assert config["pairs"][i][0] == pairs[0]["deviceB"]
        assert config["pairs"][i][1] == pairs[0]["deviceA"]


@pytest.mark.run(after="test_login")
def test_config(http_service):
    assert NUM_USERS >= 2, "NUM_USERS should be at least 2"
    users[0].client.post_config(
        users[0].devices[0].id, {"volume": 70, "brightness": 50, "language": "en"}
    )
    assert users[0].client.get_config(users[0].devices[0].id) == {
        "volume": 70,
        "brightness": 50,
        "language": "en",
    }
    users[0].client.post_config(
        users[0].devices[0].id, {"volume": 71, "brightness": 51, "language": "de"}
    )
    assert users[0].client.get_config(users[0].devices[0].id) == {
        "volume": 71,
        "brightness": 51,
        "language": "de",
    }
    with pytest.raises(ToCaroForbidden):
        users[0].client.post_config(
            users[1].devices[0].id, {"volume": 70, "brightness": 50, "language": "en"}
        )
        pytest.fail("should have failed!")
    with pytest.raises(ToCaroForbidden):
        assert users[0].client.get_config(users[1].devices[0].id) == {
            "volume": 70,
            "brightness": 50,
            "language": "en",
        }
        pytest.fail("should have failed!")


@pytest.mark.run(after="test_login")
def test_communication_without_access(http_service):
    assert NUM_PAIRS >= 2, "NUM_PAIRS should be at least 2"
    assert NUM_USERS >= 4, "NUM_USERS should be at least 4"
    payload = {"test": True}

    with pytest.raises(ToCaroForbidden):

        users[0].client.post_event(
            receiver=config["pairs"][2][1],
            sender=config["pairs"][2][0],
            payload=payload,
        )
        pytest.fail("was able to send event to not allowed device")

    events = users[2].client.get_events(deviceId=config["pairs"][2][0])
    assert len(events) == 0, "The list of events should still be empty"


# should never be executed before 'test_communication_without_access',
# since this could skew the results
@pytest.mark.run(after="test_communication_without_access")
def test_communication(http_service):
    assert NUM_USERS >= 2, "NUM_USERS should be at least 2"

    for i in range(0, NUM_USERS):
        payload = {"test": True}

        payload = random_payload()
        users[i].client.post_event(
            receiver=config["pairs"][i][1],
            sender=config["pairs"][i][0],
            payload=payload,
        )
        if i % 2 == 0:
            # get the events of the device from the next user, this should be
            # the paired device at even indexes
            events = users[i + 1].client.get_events(deviceId=config["pairs"][i][1])
        else:
            # get the events of the device from the previous user, this should
            # be the paired device at odd indexes
            events = users[i - 1].client.get_events(deviceId=config["pairs"][i][1])
        assert len(events) == 1
        assert (
            events[0]["payloadJson"] == payload
        ), "The payload of the returned event did not match the sent payload"
        assert (
            events[0]["receiverDeviceId"] == config["pairs"][i][1]
        ), "The receiver of the received event was not correct"
        assert (
            events[0]["senderDeviceId"] == config["pairs"][i][0]
        ), "The sender of the received event was not correct"
