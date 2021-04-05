from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile

import os
from PIL import Image
from io import BytesIO
from app_main.models import Team


class Command(BaseCommand):
    help = 'Loads IPL team to DB'

    def handle(self, *args, **kwargs):
        self.upload_team_table()

    @transaction.atomic
    def upload_team_table(self):
        teams = {
            'MI': {'fore_color': '#D1AB3E', 'back_color': '#083F88'},
            'PBKS': {'fore_color': '#FFF9EF', 'back_color': '#F11716'},
            'KKR': {'fore_color': '#E8A93F', 'back_color': '#563089'},
            'DC': {'fore_color': '#C52423', 'back_color': '#17479E'},
            'CSK': {'fore_color': '#0066B3', 'back_color': '#FFCC00'},
            'SRH': {'fore_color': '#F7A703', 'back_color': '#E75900'},
            'RCB': {'fore_color': '#F2E1B3', 'back_color': '#D50C14'},
            'RR': {'fore_color': '#19132D', 'back_color': '#EA1985'},
        }

        def get_img(team, typ):
            if typ == 'logo':
                img_path = os.path.join(
                    settings.BASE_DIR, 'app_main', 'static', 'img', 'logos', f"{team.lower()}.png")
            elif typ == 'slogo':
                img_path = os.path.join(
                    settings.BASE_DIR, 'app_main', 'static', 'img', 'small-logo', f"{team.lower()}.png")
            elif typ == 'bg':
                img_path = os.path.join(
                    settings.BASE_DIR, 'app_main', 'static', 'img', 'bg', f"{team.lower()}.png")
            elif typ == 'profile_bg':
                img_path = os.path.join(
                    settings.BASE_DIR, 'app_main', 'static', 'img', 'profile-bg', f"{team.upper()}.jpg")

            img = Image.open(img_path)
            buffer = BytesIO()
            img.save(buffer, format=img.format)
            buf_value = buffer.getvalue()
            pill_img = ContentFile(buf_value)
            final = InMemoryUploadedFile(
                pill_img, None, f"{team.lower()}.jpg", 'image/jpeg', pill_img.tell, None)
            return (f"{team.lower()}.jpg", final)

        # Clear the Team Table
        Team.objects.all().delete()

        for team in teams.keys():
            obj = Team.objects.create(name=team,
                                      fore_color=teams[team]['fore_color'],
                                      back_color=teams[team]['back_color'])
            obj.logo.save(*get_img(team, 'logo'))
            obj.slogo.save(*get_img(team, 'slogo'))
            obj.bg.save(*get_img(team, 'bg'))
            obj.profile_bg.save(*get_img(team, 'profile_bg'))
            obj.save()
