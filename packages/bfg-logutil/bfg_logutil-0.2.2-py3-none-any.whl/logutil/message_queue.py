import threading


class MessageQueue:
    def __init__(self, handler, defer):
        assert handler is not None
        assert defer > 0

        self.handler = handler
        self.defer = defer

        self.pending = []
        self.flushing = False
        self.lock = threading.Lock()

    def add(self, message):
        schedule = False
        with self.lock:
            self.pending.append(message)
            if not self.flushing:
                self.flushing = True
                schedule = True

        if schedule:
            timer = threading.Timer(self.defer, self.flush)
            timer.start()

    def flush(self):
        while True:
            with self.lock:
                if len(self.pending) == 0:
                    self.flushing = False
                    return
                messages = self.pending
                self.pending = []

            self.handler.write_many(messages)
