"""
Create the Tech Schedule page in ERPNext.
Run via: bench --site erp.aaairrigationservice.com execute erpnext_3cx.create_page.create_tech_schedule_page
Or directly via: bench --site ... console, then paste.
"""
import frappe

def create_tech_schedule_page():
    # Delete existing if present
    if frappe.db.exists("Page", "tech-schedule"):
        frappe.db.sql("DELETE FROM `tabPage Role` WHERE parent='tech-schedule'")
        frappe.db.sql("DELETE FROM `tabPage` WHERE name='tech-schedule'")
        frappe.db.commit()
        print("Deleted existing tech-schedule page")

    now = frappe.utils.now()
    # Insert directly to bypass developer_mode check
    frappe.db.sql("""
        INSERT INTO `tabPage` (
            name, page_name, title, module, standard, system_page,
            script, style, owner, modified_by, creation, modified, docstatus
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        "tech-schedule", "tech-schedule", "Tech Schedule", "Selling", "No", 0,
        PAGE_JS, PAGE_CSS, "Administrator", "Administrator", now, now, 0
    ))

    # Add role access
    for i, role in enumerate(["System Manager", "Sales Manager", "Sales User"]):
        frappe.db.sql("""
            INSERT INTO `tabPage Role` (name, parent, parenttype, parentfield, role, idx)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (frappe.generate_hash("", 10), "tech-schedule", "Page", "roles", role, i+1))

    frappe.db.commit()
    print("Created Page: tech-schedule (module: Selling)")
    return "tech-schedule"


PAGE_CSS = r"""
.ts-container {
	max-width: 1400px;
	margin: 0 auto;
	padding: 0 15px;
	font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.ts-header {
	text-align: center;
	padding: 10px 0 15px;
}

.ts-view-label {
	display: block;
	font-size: 11px;
	text-transform: uppercase;
	letter-spacing: 1px;
	color: #1b7abf;
	font-weight: 700;
	margin-bottom: 2px;
}

.ts-current-date {
	display: block;
	font-size: 22px;
	font-weight: 900;
	color: #1e293b;
}

.ts-grid {
	width: 100%;
	border-collapse: separate;
	border-spacing: 0;
	border: 1px solid #e2e8f0;
	border-radius: 8px;
	overflow: hidden;
	background: #fff;
	box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}

.ts-grid thead th {
	background: #1b7abf;
	color: #fff;
	padding: 12px 10px;
	font-size: 13px;
	font-weight: 700;
	text-transform: uppercase;
	letter-spacing: 0.5px;
	text-align: center;
	border-bottom: 2px solid #15649e;
}

.ts-grid thead th:first-child {
	text-align: left;
	padding-left: 16px;
}

.ts-time-col {
	width: 120px;
	min-width: 120px;
}

.ts-tech-col {
	min-width: 160px;
}

.ts-time-cell {
	background: #f8fafc;
	font-weight: 700;
	font-size: 12px;
	color: #475569;
	padding: 12px 16px;
	border-right: 1px solid #e2e8f0;
	border-bottom: 1px solid #e2e8f0;
	white-space: nowrap;
}

.ts-time-cell.ts-today {
	background: #eff6ff;
	color: #1b7abf;
	font-weight: 900;
}

.ts-today-row {
	background: #f0f9ff;
}

.ts-cell {
	padding: 8px;
	border-right: 1px solid #e2e8f0;
	border-bottom: 1px solid #e2e8f0;
	vertical-align: top;
	min-height: 70px;
}

.ts-cell:last-child {
	border-right: none;
}

.ts-cell-available {
	background: #d1fae5;
	cursor: pointer;
	text-align: center;
	vertical-align: middle;
	transition: background 0.15s;
}

.ts-cell-available:hover {
	background: #a7f3d0;
}

.ts-book-label {
	font-size: 13px;
	font-weight: 600;
	color: #059669;
}

.ts-cell-booked {
	background: #fff;
}

.ts-cell-week-booked {
	background: #fff;
	cursor: pointer;
	transition: background 0.15s;
}

.ts-cell-week-booked:hover {
	background: #f8fafc;
}

.ts-booking-card {
	display: block;
	padding: 8px 10px;
	border-radius: 6px;
	margin-bottom: 6px;
	text-decoration: none;
	transition: transform 0.1s, box-shadow 0.1s;
}

.ts-booking-card:last-child {
	margin-bottom: 0;
}

.ts-booking-card:hover {
	transform: translateY(-1px);
	box-shadow: 0 2px 8px rgba(0,0,0,0.12);
	text-decoration: none;
}

.ts-booking-customer {
	font-weight: 700;
	font-size: 13px;
	margin-bottom: 2px;
}

.ts-booking-detail {
	font-size: 11px;
	font-weight: 600;
	text-transform: uppercase;
	letter-spacing: 0.3px;
	opacity: 0.85;
}

.ts-booking-addr {
	font-size: 11px;
	opacity: 0.7;
	margin-top: 2px;
}

.ts-booking-id {
	font-size: 10px;
	opacity: 0.5;
	margin-top: 3px;
	font-family: monospace;
}

.ts-week-count {
	display: block;
	font-size: 12px;
	font-weight: 700;
	color: #1b7abf;
	margin-bottom: 6px;
}

.ts-week-item {
	padding: 4px 8px;
	margin-bottom: 3px;
	border-radius: 4px;
	font-size: 12px;
	font-weight: 500;
	white-space: nowrap;
	overflow: hidden;
	text-overflow: ellipsis;
}

.ts-unassigned-section {
	margin-top: 20px;
	border: 2px solid #f59e0b;
	border-radius: 8px;
	overflow: hidden;
	background: #fffbeb;
}

.ts-unassigned-header {
	background: #fef3c7;
	padding: 10px 16px;
	font-weight: 700;
	font-size: 14px;
	color: #92400e;
	border-bottom: 1px solid #fde68a;
}

.ts-unassigned-list {
	padding: 8px;
}

.ts-unassigned-item {
	display: flex;
	align-items: center;
	gap: 16px;
	padding: 8px 12px;
	background: #fff;
	border-radius: 6px;
	margin-bottom: 4px;
	text-decoration: none;
	color: #1e293b;
	border: 1px solid #fde68a;
	transition: background 0.15s;
}

.ts-unassigned-item:hover {
	background: #fef9c3;
	text-decoration: none;
	color: #1e293b;
}

.ts-ua-name {
	font-weight: 700;
	font-size: 13px;
	flex: 1;
}

.ts-ua-date, .ts-ua-slot {
	font-size: 12px;
	color: #64748b;
}

.ts-ua-id {
	font-size: 11px;
	font-family: monospace;
	color: #94a3b8;
}

.ts-footer {
	text-align: center;
	padding: 20px 0 10px;
	font-size: 11px;
	color: #94a3b8;
	letter-spacing: 0.5px;
}

@media (max-width: 768px) {
	.ts-grid {
		font-size: 12px;
	}
	.ts-tech-col {
		min-width: 120px;
	}
	.ts-time-col {
		width: 80px;
		min-width: 80px;
	}
	.ts-booking-card {
		padding: 6px 8px;
	}
}
"""

PAGE_JS = r"""
frappe.pages['tech-schedule'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Tech Schedule',
		single_column: true
	});

	page.schedule = new TechSchedule(page);
};

frappe.pages['tech-schedule'].on_page_show = function(wrapper) {
	if (wrapper.page && wrapper.page.schedule) {
		wrapper.page.schedule.refresh();
	}
};

class TechSchedule {
	constructor(page) {
		this.page = page;
		this.wrapper = $(page.body);
		this.current_date = frappe.datetime.get_today();
		this.view_type = 'Day';
		this.time_slots = ['9AM - 11AM', '11AM - 1PM', '1PM - 3PM', '3PM - 5PM'];
		this.techs = [];
		this.bookings = [];

		this.setup_controls();
		this.render_skeleton();
		this.refresh();
	}

	setup_controls() {
		this.page.add_button(__('\u2190 Prev'), () => {
			this.navigate(-1);
		}, { btn_class: 'btn-default btn-sm' });

		this.page.add_button(__('Today'), () => {
			this.current_date = frappe.datetime.get_today();
			this.refresh();
		}, { btn_class: 'btn-primary btn-sm' });

		this.page.add_button(__('Next \u2192'), () => {
			this.navigate(1);
		}, { btn_class: 'btn-default btn-sm' });

		this.page.add_inner_button(__('Day View'), () => {
			this.view_type = 'Day';
			this.refresh();
		});
		this.page.add_inner_button(__('Week View'), () => {
			this.view_type = 'Week';
			this.refresh();
		});
	}

	navigate(direction) {
		let d = frappe.datetime.str_to_obj(this.current_date);
		if (this.view_type === 'Week') {
			d.setDate(d.getDate() + (direction * 7));
		} else {
			d.setDate(d.getDate() + direction);
		}
		this.current_date = frappe.datetime.obj_to_str(d);
		this.refresh();
	}

	get_week_dates() {
		let d = frappe.datetime.str_to_obj(this.current_date);
		let day_of_week = d.getDay();
		let monday = new Date(d);
		monday.setDate(d.getDate() - (day_of_week === 0 ? 6 : day_of_week - 1));

		let dates = [];
		for (let i = 0; i < 7; i++) {
			let dd = new Date(monday);
			dd.setDate(monday.getDate() + i);
			dates.push(frappe.datetime.obj_to_str(dd));
		}
		return dates;
	}

	format_date_display(date_str) {
		let d = frappe.datetime.str_to_obj(date_str);
		let months = ['January','February','March','April','May','June','July','August','September','October','November','December'];
		return months[d.getMonth()] + ' ' + d.getDate() + ', ' + d.getFullYear();
	}

	format_date_short(date_str) {
		let d = frappe.datetime.str_to_obj(date_str);
		let months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
		return months[d.getMonth()] + ' ' + d.getDate();
	}

	get_day_name(date_str) {
		let d = frappe.datetime.str_to_obj(date_str);
		let days = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
		return days[d.getDay()];
	}

	tech_display_name(tech_email) {
		if (!tech_email) return 'Unassigned';
		let name = tech_email.split('@')[0];
		return name.charAt(0).toUpperCase() + name.slice(1);
	}

	get_booking_color(booking) {
		if (booking.status === 'Cancelled') return { bg: '#f3f4f6', border: '#9ca3af', text: '#6b7280' };
		let ot = (booking.order_type || '').toLowerCase();
		if (ot.includes('maintenance')) return { bg: '#fef9c3', border: '#eab308', text: '#854d0e' };
		if (ot.includes('priority') || ot.includes('emergency')) return { bg: '#fee2e2', border: '#ef4444', text: '#991b1b' };
		return { bg: '#dbeafe', border: '#3b82f6', text: '#1e40af' };
	}

	render_skeleton() {
		this.wrapper.html(
			'<div class="ts-container">' +
				'<div class="ts-header">' +
					'<div class="ts-date-display"></div>' +
				'</div>' +
				'<div class="ts-grid-wrapper"></div>' +
				'<div class="ts-unassigned-wrapper"></div>' +
				'<div class="ts-footer">Powered by Boatman Systems\u2122</div>' +
			'</div>'
		);
	}

	refresh() {
		let me = this;
		frappe.call({
			method: 'erpnext_3cx.api.get_schedule_data',
			args: {
				date: me.current_date,
				view_type: me.view_type
			},
			callback: function(r) {
				if (r.message) {
					me.techs = r.message.techs || [];
					me.bookings = r.message.bookings || [];
					me.time_slots = r.message.time_slots || me.time_slots;
					me.render();
				}
			}
		});
	}

	render() {
		if (this.view_type === 'Day') {
			this.render_day_view();
		} else {
			this.render_week_view();
		}
		this.render_unassigned();
		this.update_header();
	}

	update_header() {
		let display = '';
		if (this.view_type === 'Day') {
			display = this.format_date_display(this.current_date);
		} else {
			let dates = this.get_week_dates();
			display = this.format_date_short(dates[0]) + ' \u2013 ' + this.format_date_short(dates[6]) + ', ' +
				frappe.datetime.str_to_obj(dates[6]).getFullYear();
		}
		this.wrapper.find('.ts-date-display').html(
			'<span class="ts-view-label">' + this.view_type + ' View</span>' +
			'<span class="ts-current-date">' + display + '</span>'
		);
	}

	render_day_view() {
		let me = this;
		let techs = this.techs.length ? this.techs : ['(No technicians)'];

		let html = '<table class="ts-grid">';
		html += '<thead><tr><th class="ts-time-col">Time Slot</th>';
		techs.forEach(function(t) {
			html += '<th class="ts-tech-col">' + me.tech_display_name(t) + '</th>';
		});
		html += '</tr></thead><tbody>';

		me.time_slots.forEach(function(slot) {
			html += '<tr>';
			html += '<td class="ts-time-cell">' + slot + '</td>';
			techs.forEach(function(tech) {
				let cell_bookings = me.bookings.filter(function(b) {
					return b.custom_scheduled_date === me.current_date &&
						b.custom_scheduled_time === slot &&
						b.custom_technician === tech;
				});

				if (cell_bookings.length > 0) {
					html += '<td class="ts-cell ts-cell-booked">';
					cell_bookings.forEach(function(b) {
						let colors = me.get_booking_color(b);
						let addr = b.shipping_address_name || '';
						if (addr.length > 40) addr = addr.substring(0, 40) + '...';
						html += '<a href="/app/quotation/' + b.name + '" class="ts-booking-card" ' +
							'style="background:' + colors.bg + ';border-left:4px solid ' + colors.border + ';color:' + colors.text + ';">' +
							'<div class="ts-booking-customer">' + frappe.utils.escape_html(b.party_name || '') + '</div>' +
							'<div class="ts-booking-detail">' + frappe.utils.escape_html(b.order_type || '') + '</div>' +
							'<div class="ts-booking-addr">' + frappe.utils.escape_html(addr) + '</div>' +
							'<div class="ts-booking-id">' + b.name + '</div>' +
							'</a>';
					});
					html += '</td>';
				} else {
					let book_url = '/app/quotation/new-quotation-1?custom_scheduled_date=' +
						me.current_date + '&custom_scheduled_time=' + encodeURIComponent(slot) +
						'&custom_technician=' + encodeURIComponent(tech);
					html += '<td class="ts-cell ts-cell-available" onclick="window.location.href=\'' + book_url + '\'">' +
						'<span class="ts-book-label">+ Book</span></td>';
				}
			});
			html += '</tr>';
		});

		html += '</tbody></table>';
		this.wrapper.find('.ts-grid-wrapper').html(html);
	}

	render_week_view() {
		let me = this;
		let dates = this.get_week_dates();
		let techs = this.techs.length ? this.techs : ['(No technicians)'];

		let html = '<table class="ts-grid">';
		html += '<thead><tr><th class="ts-time-col">Day</th>';
		techs.forEach(function(t) {
			html += '<th class="ts-tech-col">' + me.tech_display_name(t) + '</th>';
		});
		html += '</tr></thead><tbody>';

		dates.forEach(function(date_str) {
			let day_name = me.get_day_name(date_str);
			let date_label = day_name + ' ' + me.format_date_short(date_str);
			let is_today = date_str === frappe.datetime.get_today();

			html += '<tr class="' + (is_today ? 'ts-today-row' : '') + '">';
			html += '<td class="ts-time-cell' + (is_today ? ' ts-today' : '') + '">' + date_label + '</td>';

			techs.forEach(function(tech) {
				let day_bookings = me.bookings.filter(function(b) {
					return b.custom_scheduled_date === date_str && b.custom_technician === tech;
				});

				if (day_bookings.length > 0) {
					html += '<td class="ts-cell ts-cell-week-booked" ' +
						'data-date="' + date_str + '">';
					html += '<span class="ts-week-count">' + day_bookings.length + ' job' +
						(day_bookings.length > 1 ? 's' : '') + '</span>';
					day_bookings.forEach(function(b) {
						let colors = me.get_booking_color(b);
						html += '<div class="ts-week-item" style="background:' + colors.bg + ';border-left:3px solid ' + colors.border + ';">' +
							frappe.utils.escape_html(b.party_name || b.name) + '</div>';
					});
					html += '</td>';
				} else {
					html += '<td class="ts-cell ts-cell-available" data-date="' + date_str + '">' +
						'<span class="ts-book-label">-</span></td>';
				}
			});
			html += '</tr>';
		});

		html += '</tbody></table>';
		this.wrapper.find('.ts-grid-wrapper').html(html);

		// Bind click handlers for week view cells
		this.wrapper.find('.ts-cell-week-booked, .ts-cell-available').on('click', function() {
			let clicked_date = $(this).data('date');
			if (clicked_date) {
				me.current_date = clicked_date;
				me.view_type = 'Day';
				me.refresh();
			}
		});
	}

	render_unassigned() {
		let me = this;
		let unassigned = [];

		if (this.view_type === 'Day') {
			unassigned = this.bookings.filter(function(b) {
				return b.custom_scheduled_date === me.current_date && !b.custom_technician;
			});
		} else {
			let dates = this.get_week_dates();
			unassigned = this.bookings.filter(function(b) {
				return dates.indexOf(b.custom_scheduled_date) >= 0 && !b.custom_technician;
			});
		}

		if (unassigned.length === 0) {
			this.wrapper.find('.ts-unassigned-wrapper').html('');
			return;
		}

		let html = '<div class="ts-unassigned-section">';
		html += '<div class="ts-unassigned-header">\u26a0 No Technician Assigned (' + unassigned.length + ')</div>';
		html += '<div class="ts-unassigned-list">';
		unassigned.forEach(function(b) {
			html += '<a href="/app/quotation/' + b.name + '" class="ts-unassigned-item">' +
				'<span class="ts-ua-name">' + frappe.utils.escape_html(b.party_name || '') + '</span>' +
				'<span class="ts-ua-date">' + (b.custom_scheduled_date || '') + '</span>' +
				'<span class="ts-ua-slot">' + (b.custom_scheduled_time || '') + '</span>' +
				'<span class="ts-ua-id">' + b.name + '</span>' +
				'</a>';
		});
		html += '</div></div>';
		this.wrapper.find('.ts-unassigned-wrapper').html(html);
	}
}
"""

if __name__ == "__main__":
    create_tech_schedule_page()
