from twitterbot.handlers import MentionEventHandler


class ActivityEventHub(object):
    event_handlers = {
        'tweet_create_events': MentionEventHandler
    }

    def handle_event(self, event):
        for event_type in self.event_handlers.keys():
            if event_type not in event:
                continue

            handler_cls = self.event_handlers[event_type]
            handler = handler_cls(
                event_data=event.get(event_type)[0],
                for_user_id=int(event.get('for_user_id')),
                original_event=event
            )
            handler.handle()
            break
