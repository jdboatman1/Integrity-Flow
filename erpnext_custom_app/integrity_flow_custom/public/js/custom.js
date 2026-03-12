// Boatman Systems™ Custom JavaScript

frappe.ready(function() {
    // Add custom branding
    console.log('Integrity Flow Custom App - Powered by Boatman Systems™');
    
    // Auto-format phone numbers
    frappe.ui.form.on('Customer', {
        mobile_no: function(frm) {
            if (frm.doc.mobile_no) {
                let digits = frm.doc.mobile_no.replace(/\D/g, '').slice(-10);
                if (digits.length === 10) {
                    frm.set_value('mobile_no', `(${digits.slice(0,3)}) ${digits.slice(3,6)}-${digits.slice(6)}`);
                }
            }
        }
    });
    
    // Quotation helpers
    frappe.ui.form.on('Quotation', {
        refresh: function(frm) {
            // Add custom button to sync to Google Calendar
            if (frm.doc.custom_scheduled_date) {
                frm.add_custom_button('Sync to Google Calendar', function() {
                    frappe.call({
                        method: 'integrity_flow_custom.api.sync_estimate_to_gcal',
                        args: {
                            quotation_id: frm.doc.name
                        },
                        callback: function(r) {
                            if (r.message && r.message.success) {
                                frappe.msgprint('Synced to Google Calendar!');
                            } else {
                                frappe.msgprint('Sync failed. Check error logs.');
                            }
                        }
                    });
                }, 'Actions');
            }
        }
    });
});
