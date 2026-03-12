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
		// Prev button
		this.page.add_button(__('← Prev'), () => {
			this.navigate(-1);
		}, { btn_class: 'btn-default btn-sm' });

		// Today button
		this.page.add_button(__('Today'), () => {
			this.current_date = frappe.datetime.get_today();
			this.refresh();
		}, { btn_class: 'btn-primary btn-sm' });

		// Next button
		this.page.add_button(__('Next →'), () => {
			this.navigate(1);
		}, { btn_class: 'btn-default btn-sm' });

		// Day/Week toggle
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
		this.wrapper.html(`
			<div class="ts-container">
				<div class="ts-header">
					<div class="ts-date-display"></div>
				</div>
				<div class="ts-grid-wrapper"></div>
				<div class="ts-unassigned-wrapper"></div>
				<div class="ts-footer">Powered by Boatman Systems\u2122</div>
			</div>
		`);
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
		// Header row
		html += '<thead><tr><th class="ts-time-col">Time Slot</th>';
		techs.forEach(function(t) {
			html += '<th class="ts-tech-col">' + me.tech_display_name(t) + '</th>';
		});
		html += '</tr></thead><tbody>';

		// Time slot rows
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
						'onclick="cur_page.page.schedule.switch_to_day(\'' + date_str + '\')">';
					html += '<span class="ts-week-count">' + day_bookings.length + ' job' +
						(day_bookings.length > 1 ? 's' : '') + '</span>';
					day_bookings.forEach(function(b) {
						let colors = me.get_booking_color(b);
						html += '<div class="ts-week-item" style="background:' + colors.bg + ';border-left:3px solid ' + colors.border + ';">' +
							frappe.utils.escape_html(b.party_name || b.name) + '</div>';
					});
					html += '</td>';
				} else {
					html += '<td class="ts-cell ts-cell-available" ' +
						'onclick="cur_page.page.schedule.switch_to_day(\'' + date_str + '\')">' +
						'<span class="ts-book-label">-</span></td>';
				}
			});
			html += '</tr>';
		});

		html += '</tbody></table>';
		this.wrapper.find('.ts-grid-wrapper').html(html);
	}

	switch_to_day(date_str) {
		this.current_date = date_str;
		this.view_type = 'Day';
		this.refresh();
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
