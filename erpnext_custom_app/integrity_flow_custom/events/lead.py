import frappe
from frappe import _

def before_save(doc, method):
    """
    Set defaults on Lead before saving
    """
    # Auto-set source if not set
    if not doc.source:
        doc.source = "Website"
    
    # Auto-set status if not set  
    if not doc.status:
        doc.status = "Open"

def after_insert(doc, method):
    """
    After Lead is created
    """
    pass
