
class Controller():    
    def __init__(self, db):
        self.db = db
        self.user_logged_in = False
        self.user_id = None