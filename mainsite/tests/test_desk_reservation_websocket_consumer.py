# from django.test import TestCase
# from django.urls import re_path

# from channels.routing import URLRouter
# from channels.testing import WebsocketCommunicator
# from mainsite.consumers import DeskReservationConsumer


# class DeskReservationWebSocketConsumerTestCase(TestCase):
#     async def test_reservation_consumer(self):
#         application = URLRouter([re_path(r"ws/desk-reservation/(?P<building>\w+)/(?P<floor>\w+)/$", DeskReservationConsumer.as_asgi())])
#         communicator = WebsocketCommunicator(application, "/ws/desk-reservation/S/1/")
#         connected, subprotocol = await communicator.connect()
#         assert connected

#         # test sending text
#         await communicator.send_json_to({"message": "refresh"})
#         response = await communicator.receive_json_from()
#         assert response.get("message") == "refresh"

#         # close
#         await communicator.disconnect()