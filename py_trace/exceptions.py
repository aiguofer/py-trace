class ApiError(Exception):
    """
    Error from the Trace API
    """

    def __init__(self, error):
        self.message = error['message']
        self.id = error['id']

    def __str__(self):
        return "{0}: {1}".format(self.id, self.message)
