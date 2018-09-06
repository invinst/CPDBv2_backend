from twitterbot.handlers import MentionEventHandler


class ActivityEventWorker(object):
    workers = {
        'tweet_create_events': MentionEventHandler
    }

    def process(self, event):
        for event_type in self.workers.keys():
            if event_type not in event:
                continue

            worker_cls = self.workers[event_type]
            worker = worker_cls(
                event_data=event.get(event_type)[0],
                for_user_id=int(event.get('for_user_id'))
            )
            worker.handle()
            break
