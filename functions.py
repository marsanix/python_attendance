from flask import session

def isAdmin():
    """
    Mengembalikan True jika user saat ini adalah admin.
    """
    return session.get('role') == 'admin'
