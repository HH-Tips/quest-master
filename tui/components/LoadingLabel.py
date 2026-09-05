from textual.widgets import Label

class LoadingLabel(Label):

    _isLoading = True
    dot_count = 0
    text = "Loading"

    def __init__(self, *args, interval = 0.5, **kwargs):
        super().__init__(*args, **kwargs)
        if len(args) >= 1:
            self.text = args[0]
        self.interval = interval

    def set_text(self, text):
        self.text = text
        self.dot_count = 0
        self.update(text)

    def set_loading(self, loading):
        self._isLoading = loading
        self.set_interval(self.interval, self.update_dots, pause=(not self._isLoading))
        self.update_dots()

    def on_mount(self):
        self.set_interval(self.interval, self.update_dots, pause=(not self._isLoading))

    def update_dots(self):
        if not self._isLoading:
            self.dot_count = 0
        else:
            self.dot_count = (self.dot_count + 1) % 4
        self.update(f"{self.text}{'.' * self.dot_count}")