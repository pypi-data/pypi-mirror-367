# Copyright (c) 2011, Canonical Ltd
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

"""Tests for AMQP receiving."""


import errno

import amqp
from oops import Config

from oops_amqp import Receiver
from oops_amqp import anybson as bson


def test_stop_on_sentinel(
    connection_factory, channel, exchange_name, queue_name
):
    # A sentinel can be used to stop the receiver (useful for testing).
    reports = []

    def capture(report):
        reports.append(report)
        return [report["id"]]

    expected_report = {"id": "foo", "otherkey": 42}
    message = amqp.Message(bson.dumps(expected_report))
    channel.basic_publish(message, exchange_name, routing_key="")
    sentinel = b"xxx"
    channel.basic_publish(
        amqp.Message(sentinel), exchange_name, routing_key=""
    )
    config = Config()
    config.publisher = capture
    receiver = Receiver(config, connection_factory, queue_name)
    receiver.sentinel = sentinel
    receiver.run_forever()
    assert reports == [expected_report]


def test_stop_via_stopping(
    connection_factory, channel, exchange_name, queue_name
):
    # Setting the stopping field should stop the run_forever loop.
    reports = []

    def capture(report):
        reports.append(report)
        return [report["id"]]

    expected_report = {"id": "foo", "otherkey": 42}
    message = amqp.Message(bson.dumps(expected_report))
    channel.basic_publish(message, exchange_name, routing_key="")
    config = Config()
    config.publisher = capture

    # We don't want to loop forever: patch the channel so that after one
    # call to wait (which will get our injected message) the loop will shut
    # down.
    def patching_factory():
        connection = connection_factory()
        old_channel = connection.channel

        def new_channel():
            result = old_channel()
            old_wait = result.wait

            def new_wait(*args, **kwargs):
                receiver.stopping = True
                return old_wait(*args, **kwargs)

            result.wait = new_wait
            return result

        connection.channel = new_channel
        return connection

    receiver = Receiver(config, patching_factory, queue_name)
    receiver.run_forever()
    assert reports == [expected_report]


def test_run_forever():
    # run_forever subscribes and then calls drain_events in a loop.
    calls = []

    class FakeChannel:
        def __init__(self, calls):
            self.calls = calls
            self.is_open = True

        def basic_consume(self, queue_name, callback=None):
            self.calls.append(("basic_consume", queue_name, callback))
            return "tag"

        def basic_cancel(self, tag):
            self.calls.append(("basic_cancel", tag))

        def close(self):
            self.is_open = False

    class FakeConnection:
        def __init__(self, calls):
            self.calls = calls

        def connect(self):
            pass

        def channel(self):
            return FakeChannel(calls)

        def drain_events(self, timeout=None):
            self.calls.append(("drain_events", timeout))
            if len(self.calls) > 2:
                receiver.stopping = True

        def close(self):
            pass

    receiver = Receiver(None, lambda: FakeConnection(calls), "foo")
    receiver.run_forever()
    assert calls == [
        ("basic_consume", "foo", receiver.handle_report),
        ("drain_events", 1),
        ("drain_events", 1),
        ("basic_cancel", "tag"),
    ]


def test_tolerates_amqp_trouble(
    connection_factory, channel, exchange_name, queue_name
):
    # If the AMQP server is unavailable for a short period, the receiver
    # will automatically reconnect.
    # Break a connection to raise socket.error (which we know from the
    # publisher tests is what leaks through when rabbit is shutdown).
    # We raise it the first time on each amqp method call.
    reports = []

    def capture(report):
        reports.append(report)
        return [report["id"]]

    expected_report = {"id": "foo", "otherkey": 42}
    message = amqp.Message(bson.dumps(expected_report))
    channel.basic_publish(message, exchange_name, routing_key="")
    config = Config()
    config.publisher = capture
    state = {}

    def error_once(func):
        def wrapped(*args, **kwargs):
            func_ref = func.__code__
            if func_ref in state:
                return func(*args, **kwargs)
            else:
                state[func_ref] = True
                # Use EPIPE because the close() code checks that (though
                # the rest doesn't)
                raise OSError(errno.EPIPE, "booyah")

        return wrapped

    @error_once
    def patching_factory():
        connection = connection_factory()
        old_channel = connection.channel

        @error_once
        def new_channel():
            result = old_channel()
            result.basic_consume = error_once(result.basic_consume)
            result.basic_cancel = error_once(result.basic_cancel)
            result.close = error_once(result.close)
            return result

        connection.channel = new_channel
        connection.drain_events = error_once(connection.drain_events)
        connection.close = error_once(connection.close)
        return connection

    receiver = Receiver(config, patching_factory, queue_name)
    receiver.sentinel = b"arhh"
    channel.basic_publish(amqp.Message(b"arhh"), exchange_name, routing_key="")
    receiver.run_forever()
    assert reports == [expected_report]
