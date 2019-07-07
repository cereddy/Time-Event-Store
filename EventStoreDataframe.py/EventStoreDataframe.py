
DEFAULT_DATAFRAME = "dataframe"

class EventStoreDataframe:

    def __init__(self, dataframe=None, mode="rw"):

        if dataframe:
            self.dataframe = dataframe
        else:
