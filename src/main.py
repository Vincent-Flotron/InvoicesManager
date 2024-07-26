from views import MainApp

import sqlite3
import os

if __name__ == "__main__":
    # Get the directory path of the current script
    script_dir       = os.path.dirname( os.path.abspath(__file__) )
    absolute_db_path = os.path.join( script_dir + "/..",
                                     "data/database.db" )
    conn             = sqlite3.connect( absolute_db_path,
                                        check_same_thread=False )
    app              = MainApp(conn,
                               absolute_db_path)
    app.mainloop()
