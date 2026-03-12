
@frappe.whitelist()
def get_schedule_data(date=None, view_type='Day'):
    """Return technician schedule data for the Tech Schedule page."""
    import datetime as dt

    if not date:
        date = frappe.utils.today()

    # Calculate date range based on view type
    target = frappe.utils.getdate(date)

    if view_type == 'Week':
        # Monday of the week
        day_of_week = target.weekday()
        start_date = target - dt.timedelta(days=day_of_week)
        end_date = start_date + dt.timedelta(days=6)
    else:
        start_date = target
        end_date = target

    time_slots = ['9AM - 11AM', '11AM - 1PM', '1PM - 3PM', '3PM - 5PM']

    # Get distinct technicians who have any bookings
    tech_rows = frappe.db.sql("""
        SELECT DISTINCT custom_technician
        FROM `tabQuotation`
        WHERE custom_technician IS NOT NULL
          AND custom_technician != ''
          AND docstatus != 2
        ORDER BY custom_technician
    """, as_list=True)

    techs = [r[0] for r in tech_rows] if tech_rows else []

    # Get bookings in date range
    bookings = frappe.db.sql("""
        SELECT
            name, party_name, custom_scheduled_date,
            custom_scheduled_time, custom_scheduled_time_open,
            custom_technician, order_type, status,
            shipping_address_name
        FROM `tabQuotation`
        WHERE docstatus != 2
          AND custom_scheduled_date IS NOT NULL
          AND custom_scheduled_date BETWEEN %s AND %s
        ORDER BY custom_scheduled_date, custom_scheduled_time
    """, (start_date, end_date), as_dict=True)

    # Convert date objects to strings for JSON serialization
    for b in bookings:
        if b.get('custom_scheduled_date'):
            b['custom_scheduled_date'] = str(b['custom_scheduled_date'])

    return {
        'techs': techs,
        'bookings': bookings,
        'time_slots': time_slots
    }
