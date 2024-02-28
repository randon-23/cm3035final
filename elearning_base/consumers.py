import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from .models import Enrollments

class ChatConsumer(AsyncWebsocketConsumer):
    def connect(self):
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        #echo message back to the client
        self.send(text_data=json.dumps({
            'message': message
        }))

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user, self.enrolled_courses = await self.get_users_and_courses()

        if self.user.is_authenticated:
            user_specific_group = f"user_notifications_{self.user.user_id}"
            await self.channel_layer.group_add(user_specific_group, self.channel_name)

            # Teacher notifications
            if self.user.is_teacher:
                teacher_group = f"enrollment_notifications_{self.user.user_id}"
                await self.channel_layer.group_add(teacher_group, self.channel_name)
            
            # Student notifications
            for course_id in self.enrolled_courses:
                material_group = f"new_material_notifications_{course_id}"
                activity_group = f"new_activity_notifications_{course_id}"
                await self.channel_layer.group_add(material_group, self.channel_name)
                await self.channel_layer.group_add(activity_group, self.channel_name)

            await self.accept()

    async def disconnect(self, close_code):
        self.user, self.enrolled_courses = await self.get_users_and_courses()

        if self.user.is_authenticated:
            user_specific_group = f"user_notifications_{self.user.user_id}"
            await self.channel_layer.group_discard(user_specific_group, self.channel_name)

            # Teacher notifications
            if self.user.is_teacher:
                teacher_group = f"enrollment_notifications_{self.user.user_id}"
                await self.channel_layer.group_discard(teacher_group, self.channel_name)
            
            # Student notifications
            for course_id in self.enrolled_courses:
                material_group = f"new_material_notifications_{course_id}"
                activity_group = f"new_activity_notifications_{course_id}"
                await self.channel_layer.group_discard(material_group, self.channel_name)
                await self.channel_layer.group_discard(activity_group, self.channel_name)

    async def new_notification(self, event):
        message = event["message"]
        title = event["title"]
        await self.send(text_data=json.dumps({
            "message": message,
            "title": title
        }))

    async def dynamic_subscription(self, event):
        material_group = event["material_group"]
        activity_group = event["activity_group"]
        await self.channel_layer.group_add(material_group, self.channel_name)
        await self.channel_layer.group_add(activity_group, self.channel_name)

        await self.send(text_data=json.dumps({
            "material_group": material_group,
            "activity_group": activity_group
        }))
    
    #The following methods are for synchronous database operations
    #And data required in async functions
    #Converting to list for immediate execution in async environment
    @database_sync_to_async
    def get_users_and_courses(self):
        user = self.scope["user"]
        enrolled_courses = Enrollments.objects.filter(student=user).values_list('course_id', flat=True)
        return user, list(enrolled_courses)