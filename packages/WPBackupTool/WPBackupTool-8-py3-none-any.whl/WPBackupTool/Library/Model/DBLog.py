class DBLog:
    def __init__(self):
        self.successful = []
        self.errors = []
        pass

    def success(self, name):
        self.successful.append(name)

    def error(self, name):
        self.errors.append(name)

    def was_success(self):
        return len(self.errors) is 0

    def to_string(self, html=False):
        new_line = "\n"
        if html:
            new_line = "<br>"

        return new_line+"-Erfolgreiche Übertragungen: " + str(self.successful)+\
            new_line+"-Fehlerhafte Übertragungen: " + str(self.errors)