telegrambot.bot_views.generic import TemplateCommandView
from django.shortcuts import render

# Create your views here.
class StartCommandView(TemplateCommandView):
    template_text = "templates/messages/command_start_text.txt"

class HelpCommandView(TemplateCommandView):
    template_text = "templates/messages/command_help_text.txt"
