import ipywidgets as widgets


class ErrorOutputManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.error_output = widgets.Output(
                layout=widgets.Layout(
                    width="800px",
                    height="100px",
                    overflow="auto",
                    border="1px solid red",
                    padding="10px",
                    display="none",
                )
            )
        return cls._instance

    def display_error(self, message):
        self.error_output.layout.display = "block"
        with self.error_output:
            self.error_output.clear_output(wait=True)
            print(f"Error: {message}")

    def clear_error(self):
        with self.error_output:
            self.error_output.clear_output(wait=True)
        self.error_output.layout.display = "none"

    def get_error_output(self):
        return self.error_output
