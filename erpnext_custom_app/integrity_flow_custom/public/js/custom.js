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
        onload: function(frm) {
            // Default order type to Service
            if (frm.is_new() && !frm.doc.order_type) {
                frm.set_value('order_type', 'Service');
            }
        },
        party_name: function(frm) {
            if (frm.doc.party_name) {
                // Fetch customer/lead address
                let doctype = frm.doc.quotation_to === 'Customer' ? 'Customer' : 'Lead';
                frappe.db.get_doc(doctype, frm.doc.party_name).then(doc => {
                    let city = '';
                    let addr = '';
                    
                    if (doctype === 'Customer') {
                        city = doc.custom_city || '';
                        addr = `${doc.custom_address_line1 || ''}\n${doc.custom_city || ''}, ${doc.custom_state || ''} ${doc.custom_zip || ''}`;
                    } else {
                        city = doc.custom_city || '';
                        addr = `${doc.custom_address_line1 || ''}\n${doc.custom_city || ''}, ${doc.custom_state || ''} ${doc.custom_zip || ''}`;
                    }
                    
                    if (addr.trim()) {
                        frm.set_value('custom_service_address', addr.trim());
                    }
                    
                    // Auto-add line items if empty
                    if (frm.doc.items.length === 0) {
                        let item_name = (city.toLowerCase() === 'frisco') ? 'Frisco Inspection' : 'System Check';
                        let rate = (city.toLowerCase() === 'frisco') ? 125 : 95;
                        
                        let child = frm.add_child('items');
                        frappe.model.set_value(child.doctype, child.name, 'item_code', item_name);
                        frappe.model.set_value(child.doctype, child.name, 'qty', 1);
                        frappe.model.set_value(child.doctype, child.name, 'rate', rate);
                        frm.refresh_field('items');
                    }
                });
            }
        },
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
