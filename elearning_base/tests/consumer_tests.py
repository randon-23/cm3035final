from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from channels.routing import URLRouter
from channels.auth import AuthMiddlewareStack
from elearning_base.routing import websocket_urlpatterns
from django.test import TransactionTestCase
from elearning_base.models import Course, Enrollments
from channels.layers import get_channel_layer
from asgiref.sync import sync_to_async
from elearning_base.models import LobbyMessage
import asyncio

User = get_user_model()

class TestNotificationConsumer(TransactionTestCase):
    async def asyncSetUp(self):
        self.student = await sync_to_async(User.objects.create_user)(username="test_student", password="test_password", email="test_student@test.com", is_teacher=False)
        self.teacher = await sync_to_async(User.objects.create_user)(username="test_teacher", password="test_password", email="test_teacher@test.com", is_teacher=True)

        self.course = await sync_to_async(Course.objects.create)(course_title="Test Course", teacher=self.teacher)
        self.enrollment = await sync_to_async(Enrollments.objects.create)(student=self.student, course=self.course)
    
    async def test_notification_consumer_connected(self):
        await self.asyncSetUp()
        communicator = WebsocketCommunicator(AuthMiddlewareStack(URLRouter(websocket_urlpatterns)), f"ws/notifications/")
        communicator.scope["user"] = self.student

        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        await communicator.disconnect()

    async def test_dynamic_subscription(self):
        await self.asyncSetUp()
        communicator = WebsocketCommunicator(AuthMiddlewareStack(URLRouter(websocket_urlpatterns)), f"ws/notifications/")
        communicator.scope["user"] = self.student

        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Test student subscription to course-specific notifications
        channel_layer = get_channel_layer()
        user_group = f"user_notifications_{self.student.user_id}"
        material_group = f"new_material_notifications_{self.course.course_id}"
        activity_group = f"new_activity_notifications_{self.course.course_id}"

        await channel_layer.group_send(user_group, {
            "type": "dynamic.subscription", 
            "material_group": material_group, 
            "activity_group": activity_group
        })

        response = await communicator.receive_json_from()
        self.assertEqual(response["material_group"], material_group)
        self.assertEqual(response["activity_group"], activity_group)

        await communicator.disconnect()

    async def test_material_notification(self):
        await self.asyncSetUp()
        communicator = WebsocketCommunicator(AuthMiddlewareStack(URLRouter(websocket_urlpatterns)), f"ws/notifications/")
        communicator.scope["user"] = self.student

        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        channel_layer = get_channel_layer()
        material_group = f"new_material_notifications_{self.course.course_id}"
        await channel_layer.group_send(material_group, {
            "type": "new.notification",
            "message": "New material added",
            "title": "New Material"
        })

        response = await communicator.receive_json_from()
        self.assertEqual(response["message"], "New material added")
        self.assertEqual(response["title"], "New Material")

        await communicator.disconnect()
    
    async def test_notification_consumer(self):
        await self.asyncSetUp()
        communicator = WebsocketCommunicator(AuthMiddlewareStack(URLRouter(websocket_urlpatterns)), f"ws/notifications/")
        communicator.scope["user"] = self.student

        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        channel_layer = get_channel_layer()
        activity_group = f"new_activity_notifications_{self.course.course_id}"
        await channel_layer.group_send(activity_group, {
            "type": "new.notification",
            "message": "New activity added",
            "title": "New Activity"
        })

        response = await communicator.receive_json_from()
        self.assertEqual(response["message"], "New activity added")
        self.assertEqual(response["title"], "New Activity")

        await communicator.disconnect()

class TestChatConsumer(TransactionTestCase):
    async def asyncSetUp(self):
        self.student = await sync_to_async(User.objects.create_user)(username="test_student", password="test_password", email="test_student@test.com", is_teacher=False)
        self.teacher = await sync_to_async(User.objects.create_user)(username="test_teacher", password="test_password", email="test_teacher@test.com", is_teacher=True)

    async def test_chat_consumer_connected(self):
        await self.asyncSetUp()
        lobby_communicator = WebsocketCommunicator(AuthMiddlewareStack(URLRouter(websocket_urlpatterns)), f"ws/lobby/")
        lobby_communicator.scope["user"] = self.student

        connected, _ = await lobby_communicator.connect()
        self.assertTrue(connected)

        await lobby_communicator.disconnect() 

    async def test_chat_message(self):
        await self.asyncSetUp()
        lobby_communicator = WebsocketCommunicator(AuthMiddlewareStack(URLRouter(websocket_urlpatterns)), f"ws/lobby/")
        lobby_communicator.scope["user"] = self.student

        connected, _ = await lobby_communicator.connect()
        self.assertTrue(connected)

        channel_layer = get_channel_layer()
        lobby_group = f'public_lobby'
        await channel_layer.group_send(lobby_group, {
            "type": "chat.message",
            "message": "Test message",
            "username": self.student.username,
            "is_teacher": self.student.is_teacher
        })

        response = await lobby_communicator.receive_json_from()
        self.assertEqual(response["message"], "Test message")
        self.assertEqual(response["username"], self.student.username)
        self.assertEqual(response["is_teacher"], self.student.is_teacher)

        await lobby_communicator.disconnect()
    
    async def test_chat_notification(self):
        await self.asyncSetUp()
        notifications_communicator = WebsocketCommunicator(AuthMiddlewareStack(URLRouter(websocket_urlpatterns)), f"ws/notifications/")

        notifications_communicator.scope["user"] = self.student

        connected, _ = await notifications_communicator.connect()

        self.assertTrue(connected)

        channel_layer = get_channel_layer()
        chat_notifications_group = f"chat_notifications"
        await channel_layer.group_send(chat_notifications_group, {
            "type": "chat.notification",
            "message": "New message in the public lobby"
        })

        response = await notifications_communicator.receive_json_from()
        self.assertEqual(response["message"], "New message in the public lobby")

    #This test involves the NotificationConsumer and ChatConsumer because it is the notificaiton consumer which sends the chat.notification event
    #to the chat_notifications group and which contains a client side checking mechanism to assess whether the user is in chat page or not
    async def test_discard_from_chat_notifications_group_upon_opening_chat_consumer(self):
        await self.asyncSetUp()
        notifications_communicator = WebsocketCommunicator(AuthMiddlewareStack(URLRouter(websocket_urlpatterns)), f"ws/notifications/")

        notifications_communicator.scope["user"] = self.student

        notifications_connected, _ = await notifications_communicator.connect()
        self.assertTrue(notifications_connected)

        channel_layer = get_channel_layer()
        chat_notifications_group = f"chat_notifications"
        await channel_layer.group_send(chat_notifications_group, {
            "type": "chat.notification",
            "message": "New message in the public lobby"
        })

        response = await notifications_communicator.receive_json_from()
        self.assertEqual(response["message"], "New message in the public lobby")

        lobby_communicator = WebsocketCommunicator(AuthMiddlewareStack(URLRouter(websocket_urlpatterns)), f"ws/lobby/")
        lobby_communicator.scope["user"] = self.student

        lobby_connected, _ = await lobby_communicator.connect()
        self.assertTrue(lobby_connected)

        await notifications_communicator.send_json_to({
            "command": "leave_chat_notifications"
        })

        await channel_layer.group_send(chat_notifications_group, {
            "type": "chat.notification",
            "message": "New message in the public lobby"
        })

        try:
            await notifications_communicator.receive_nothing(timeout=1)
            message_received = False
        except AssertionError:
            message_received = True

        self.assertFalse(message_received, "Message received after leaving the chat_notifications group")

        await lobby_communicator.disconnect()

        await notifications_communicator.send_json_to({
            "command": "join_chat_notifications"
        })

        await channel_layer.group_send(chat_notifications_group, {
            "type": "chat.notification",
            "message": "New message in the public lobby"
        })

        response = await notifications_communicator.receive_json_from()
        self.assertEqual(response["message"], "New message in the public lobby")

        await notifications_communicator.disconnect()

    async def test_message_broadcast_to_multiple_users(self):
        await self.asyncSetUp()
        student_communicator = WebsocketCommunicator(AuthMiddlewareStack(URLRouter(websocket_urlpatterns)), f"ws/lobby/")
        student_communicator.scope["user"] = self.student
        await student_communicator.connect()

        teacher_communicator = WebsocketCommunicator(AuthMiddlewareStack(URLRouter(websocket_urlpatterns)), f"ws/lobby/")
        teacher_communicator.scope["user"] = self.teacher
        await teacher_communicator.connect()

        channel_layer = get_channel_layer()
        lobby_group = f'public_lobby'
        test_message = {"message": "Hello, world!", "username": self.student.username, "is_teacher": self.student.is_teacher, 'type': "chat.message"}
        await channel_layer.group_send(lobby_group, test_message)

        expected_message = {"message": "Hello, world!", "username": self.student.username, "is_teacher": self.student.is_teacher}
        response1 = await student_communicator.receive_json_from()
        response2 = await teacher_communicator.receive_json_from()

        self.assertEqual(response1, expected_message)
        self.assertEqual(response2, expected_message)

        await student_communicator.disconnect()
        await teacher_communicator.disconnect()
    
    async def test_lobby_message_created(self):
        await self.asyncSetUp()
        communicator = WebsocketCommunicator(AuthMiddlewareStack(URLRouter(websocket_urlpatterns)), f"ws/lobby/")
        communicator.scope["user"] = self.student

        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        test_msg = {
            "message": "THIS IS A TEST MESSAGE!!"
        }
        
        await communicator.send_json_to(test_msg)
        await asyncio.sleep(1)

        message_created = await sync_to_async(LobbyMessage.objects.filter(message=test_msg['message']).exists)()
        self.assertTrue(message_created)

        await communicator.disconnect()
        

        





