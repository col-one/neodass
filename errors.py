
class NotUnique(Exception):
    def __init__(self, *args):
        super(NotUnique, self).__init__(*args)
