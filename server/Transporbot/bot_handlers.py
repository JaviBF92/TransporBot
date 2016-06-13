urlpatterns = [command('start', ),
           command('help', ),
           regex(r'(?P<org>\w+)_(?P<dst>\w+)', AuthorName.as_command_view()),
          ]
