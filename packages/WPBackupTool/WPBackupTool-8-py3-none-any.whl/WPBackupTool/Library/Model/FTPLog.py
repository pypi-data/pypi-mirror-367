class FTPLog:
    def __init__(self):
        self.successful = 0
        self.errors = 0
        self.error_filenames = []

    def success(self, num):
        self.successful += num

    def error(self, num):
        self.errors += num

    def error_files(self, files):
        self.error_filenames.extend(files)

    def was_success(self):
        return self.errors is 0 and len(self.error_filenames) is 0

    def to_string(self, html=False):
        new_line = "\n"
        if html:
            new_line = "<br>"

        return new_line+"-Erfolgreiche Übertragungen: " + str(self.successful) + \
               new_line+"-Fehlerhafte Übertragungen: " + str(self.errors) + \
               new_line+"-Fehlerhafte Dateien: " + str(self.error_filenames)