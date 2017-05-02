from mysql.connector import MySQLConnection, Error
from python_mysql_dbconfig import read_db_config

def call_procedure(proc, args):
    """
    Calls any stored procedure that adds a row returning it's id.
    """
    db_config = read_db_config()
    conn = MySQLConnection(**db_config)
    cursor = conn.cursor()
    try:
        result_args = cursor.callproc(proc, args)
        # Important, otherwise we will not see the insertions
        conn.commit()

        # The last will have the id.
        return result_args[-1]
    except Error as e:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()
