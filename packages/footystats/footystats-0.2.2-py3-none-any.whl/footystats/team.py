#team.py

class Team:
    def __init__(self):
        self._ladder        = None
        self._homeladder    = None
        self._awayladder    = None
        self._form          = None
        # self._squad         = {}

    @property
    def ladder(self):
        return self._ladder

    @ladder.setter
    def ladder(self, value):
        if not isinstance(value, int):
            raise TypeError("Ladder must be an integer")
        if value < 0:
            raise ValueError("Ladder must be greater than 0")
        self._ladder = value

    @property
    def homeladder(self):
        return self._homeladder

    @homeladder.setter
    def homeladder(self, value):
        if not isinstance(value, int):
            raise TypeError("Home ladder must be an integer")
        if value < 0:
            raise ValueError("Homeladder must be greater than 0")
        self._homeladder = value

    @property
    def awayladder(self):
        return self._awayladder

    @awayladder.setter
    def awayladder(self, value):
        if not isinstance(value, int):
            raise TypeError("Awayladder must be an integer")
        if value < 0:
            raise ValueError("Awayladder must be greater than 0")
        self._awayladder = value

    @property
    def form(self):
        return self._form

    @form.setter
    def form(self, value):
        if not isinstance(value, int):
            raise TypeError("Form must be an integer")
        if value < 0:
            raise ValueError("Form must be greater than 0")
        self._form = value

    # @property
    # def squad(self):
        # return self._squad

    # @squad.setter
    # def squad(self, value):
        # if not isinstance(value, list):
            # raise ValueError("Squad must be a list")
        # self._squad = value
