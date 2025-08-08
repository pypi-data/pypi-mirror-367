# Copyright (C) 2011-2022, Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, version 3 only.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# GNU Lesser General Public License version 3 (see the file LICENSE).

import itertools
from functools import partial

import amqp
import kombu
import pytest
from rabbitfixture.server import RabbitServer

from oops_amqp.utils import close_ignoring_connection_errors

_unique_id_gen = itertools.count(1)


@pytest.fixture
def get_unique_integer():
    def get():
        return next(_unique_id_gen)

    return get


@pytest.fixture
def get_unique_string(get_unique_integer):
    def get(prefix):
        return f"{prefix}-{get_unique_integer()}"

    return get


@pytest.fixture(scope="session")
def rabbit():
    rabbit = RabbitServer()
    rabbit.setUp()
    try:
        yield rabbit
    finally:
        rabbit.cleanUp()


@pytest.fixture(params=["amqp", "kombu"])
def connection_factory(rabbit, request):
    if request.param == "amqp":
        return partial(
            amqp.Connection,
            host=f"{rabbit.config.hostname}:{rabbit.config.port}",
            userid="guest",
            password="guest",
            virtual_host="/",
        )
    else:
        return partial(
            kombu.Connection,
            hostname=rabbit.config.hostname,
            userid="guest",
            password="guest",
            virtual_host="/",
            port=rabbit.config.port,
        )


@pytest.fixture
def connection(connection_factory):
    connection = connection_factory()
    connection.connect()
    try:
        yield connection
    finally:
        close_ignoring_connection_errors(connection)


@pytest.fixture
def channel(connection):
    channel = connection.channel()
    try:
        yield channel
    finally:
        close_ignoring_connection_errors(channel)


@pytest.fixture
def exchange_name(channel, get_unique_string):
    exchange_name = get_unique_string("exchange")
    channel.exchange_declare(
        exchange=exchange_name, type="fanout", durable=True, auto_delete=False
    )
    try:
        yield exchange_name
    finally:
        channel.exchange_delete(exchange_name)


@pytest.fixture
def queue_name(channel, exchange_name):
    queue_name, _, _ = channel.queue_declare(durable=True, auto_delete=False)
    try:
        channel.queue_bind(queue_name, exchange_name)
        yield queue_name
    finally:
        channel.queue_delete(queue_name)
