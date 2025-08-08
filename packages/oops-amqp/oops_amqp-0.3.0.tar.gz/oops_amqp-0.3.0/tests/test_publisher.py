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

"""Tests for AMQP publishing."""


from hashlib import md5

from oops_amqp import Publisher
from oops_amqp import anybson as bson


def test_publish_inherit_id(
    connection_factory, channel, exchange_name, queue_name
):
    # OOPS IDs can be set outside of Publisher().
    publisher = Publisher(
        connection_factory, exchange_name, "", inherit_id=True
    )
    reference_oops = {"id": "kept", "akey": "avalue"}
    oops = dict(reference_oops)
    expected_id = "kept"
    oops_ids = publisher(oops)
    # Publication returns the oops ID allocated.
    assert oops_ids == [expected_id]
    # The oops should not be altered by publication.
    assert oops == reference_oops

    # The received OOPS should have the ID embedded and be a bson dict.
    def check_oops(msg):
        body = msg.body
        if not isinstance(body, bytes):
            body = body.encode(msg.content_encoding or "UTF-8")
        assert bson.loads(body) == reference_oops
        channel.basic_ack(msg.delivery_tag)
        channel.basic_cancel(queue_name)

    channel.basic_consume(
        queue_name, callback=check_oops, consumer_tag=queue_name
    )
    channel.connection.drain_events()


def test_publish(connection_factory, channel, exchange_name, queue_name):
    # Publishing an oops sends it to the exchange, making a connection as
    # it goes.
    publisher = Publisher(connection_factory, exchange_name, "")
    reference_oops = {"akey": "avalue"}
    oops = dict(reference_oops)
    id_bson = md5(bson.dumps(oops)).hexdigest()
    expected_id = "OOPS-%s" % id_bson
    oops_ids = publisher(oops)
    # Publication returns the oops ID allocated.
    assert oops_ids == [expected_id]
    # The oops should not be altered by publication.
    assert oops == reference_oops
    # The received OOPS should have the ID embedded and be a bson dict.
    expected_oops = dict(reference_oops)
    expected_oops["id"] = oops_ids[0]

    def check_oops(msg):
        body = msg.body
        if not isinstance(body, bytes):
            body = body.encode(msg.content_encoding or "UTF-8")
        assert bson.loads(body) == expected_oops
        channel.basic_ack(msg.delivery_tag)
        channel.basic_cancel(queue_name)

    channel.basic_consume(
        queue_name, callback=check_oops, consumer_tag=queue_name
    )
    channel.connection.drain_events()


def test_publish_amqp_already_down(
    rabbit, connection_factory, channel, get_unique_string
):
    # If amqp is down when a connection is attempted, None is returned to
    # indicate that publication failed - and publishing after it comes back
    # works.
    # The private method use and the restart of rabbit before it gets torn
    # down are bugs in rabbitfixture that will be fixed in a future
    # release.
    exchange_name = get_unique_string("exchange")
    channel.exchange_declare(
        exchange=exchange_name, type="fanout", durable=True, auto_delete=False
    )
    try:
        rabbit.runner._stop()
        try:
            publisher = Publisher(connection_factory, exchange_name, "")
            oops = {"akey": 42}
            assert publisher(oops) == []
        finally:
            rabbit.runner._start()
            connection = connection_factory()
            connection.connect()
            channel = connection.channel()
        assert publisher(oops) != []
    finally:
        channel.exchange_delete(exchange_name)


def test_publish_amqp_down_after_use(
    rabbit, connection_factory, channel, get_unique_string
):
    # If amqp goes down after its been successfully used, None is returned
    # to indicate that publication failed - and publishing after it comes
    # back works.
    exchange_name = get_unique_string("exchange")
    channel.exchange_declare(
        exchange=exchange_name, type="fanout", durable=True, auto_delete=False
    )
    try:
        publisher = Publisher(connection_factory, exchange_name, "")
        oops = {"akey": 42}
        assert publisher(oops) is not None
        # The private method use and the restart of rabbit before it gets
        # torn down are bugs in rabbitfixture that will be fixed in a future
        # release.
        rabbit.runner._stop()
        try:
            assert publisher(oops) == []
        finally:
            rabbit.runner._start()
            connection = connection_factory()
            connection.connect()
            channel = connection.channel()
        assert publisher(oops) != []
    finally:
        channel.exchange_delete(exchange_name)
