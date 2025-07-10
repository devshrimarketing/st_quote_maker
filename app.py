import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json
import os
from utils.pdf_generator import generate_quotation_pdf
from utils.calculations import calculate_totals
from data.quotations import init_session_state, save_quotation, get_quotations

# Page configuration
st.set_page_config(page_title="Quotation Generator",
                   page_icon="📄",
                   layout="wide")

# Initialize session state
init_session_state()

# Main title
st.title("📄 Professional Quotation Generator")

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Select Page", ["Create Quotation", "Manage Quotations", "Configuration"],
    index=0)

if page == "Create Quotation":
    st.header("Create New Quotation")

    # Create two columns for better layout
    col1, col2 = st.columns([2, 1])

    with col1:
        # Customer Information Section
        st.subheader("Customer Information")

        client_name = st.text_input("Customer Name",
                                    placeholder="M/s. Customer Name")
        client_address = st.text_area("Customer Address",
                                      placeholder="Customer Address")

        col_cust1, col_cust2 = st.columns(2)
        with col_cust1:
            client_contact_person = st.text_input("Contact Person",
                                                  placeholder="Mr./Ms. Name")
            client_email = st.text_input("Email",
                                         placeholder="customer@email.com")
        with col_cust2:
            client_phone = st.text_input("Customer Phone",
                                         placeholder="+91-XXXXXXXXXX")

        # Quotation Details
        st.subheader("Quotation Details")

        col_q1, col_q2 = st.columns(2)
        with col_q1:
            quote_ref = st.text_input(
                "Quote Reference",
                value=
                f"Q{datetime.now().strftime('%Y%m%d')}{len(st.session_state.quotations) + 1:03d}"
            )
            subject = st.text_input("Subject",
                                    placeholder="Offer for Supply of...")
        with col_q2:
            # Date validation - only current and back-dated (up to 25 days)
            today = datetime.now().date()
            min_date = today - timedelta(days=25)
            quote_date = st.date_input("Quote Date",
                                       value=today,
                                       min_value=min_date,
                                       max_value=today)
            validity_days = st.number_input("Validity (Days)",
                                            min_value=1,
                                            value=15)

        # Line Items Section
        st.subheader("Line Items")

        # Initialize line items in session state if not exists
        if 'current_line_items' not in st.session_state:
            st.session_state.current_line_items = []

        # Add new line item form
        with st.expander("Add New Line Item", expanded=True):
            col_item1, col_item2 = st.columns(2)
            with col_item1:
                item_part_no = st.text_input("Item", key="new_part_no")
                item_description = st.text_area("Description",
                                                key="new_description")
                item_hsn = st.text_input("HSN Code", key="new_hsn")
                item_delivery = st.number_input("Delivery (weeks)",
                                                min_value=1,
                                                value=4,
                                                key="new_delivery")
            with col_item2:
                item_qty = st.number_input("Quantity",
                                           min_value=1,
                                           value=1,
                                           key="new_qty")
                item_unit_price = st.number_input("Unit Price (₹)",
                                                  min_value=0.0,
                                                  value=0.0,
                                                  step=0.01,
                                                  key="new_unit_price")
                item_discount = st.number_input("Item Discount (%)",
                                                min_value=0.0,
                                                max_value=100.0,
                                                value=0.0,
                                                step=0.1,
                                                key="new_discount")

            if st.button("Add Item", type="primary"):
                if item_part_no and item_description and item_qty > 0 and item_unit_price > 0:
                    # Calculate total price with discount
                    gross_amount = item_qty * item_unit_price
                    discount_amount = gross_amount * (item_discount / 100)
                    total_price = gross_amount - discount_amount

                    new_item = {
                        'part_no': item_part_no,
                        'description': item_description,
                        'hsn': item_hsn,
                        'qty': item_qty,
                        'unit_price': item_unit_price,
                        'delivery_weeks': item_delivery,
                        'discount_percent': item_discount,
                        'discount_amount': discount_amount,
                        'total_price': total_price
                    }
                    st.session_state.current_line_items.append(new_item)
                    st.success("Item added successfully!")
                    st.rerun()
                else:
                    st.error(
                        "Please fill in all required fields with valid values."
                    )

        # Display current line items
        if st.session_state.current_line_items:
            st.subheader("Current Line Items")

            # Create DataFrame for display
            df = pd.DataFrame(st.session_state.current_line_items)

            # Display items with edit/delete options
            for idx, item in enumerate(st.session_state.current_line_items):
                with st.container():
                    col_display1, col_display2, col_actions = st.columns(
                        [3, 2, 1])

                    with col_display1:
                        st.write(
                            f"**{item['part_no']}** - {item['description']}")
                        st.write(f"HSN: {item['hsn']}")
                        if item.get('delivery_weeks'):
                            st.write(
                                f"Delivery: {item['delivery_weeks']} weeks")

                    with col_display2:
                        st.write(f"Qty: {item['qty']}")
                        st.write(f"Unit Price: ₹{item['unit_price']:,.2f}")
                        if item.get('discount_percent', 0) > 0:
                            st.write(
                                f"Discount: {item['discount_percent']:.1f}%")
                        st.write(f"**Total: ₹{item['total_price']:,.2f}**")

                    with col_actions:
                        if st.button("🗑️",
                                     key=f"delete_{idx}",
                                     help="Delete item"):
                            st.session_state.current_line_items.pop(idx)
                            st.rerun()

                    st.divider()

        # Terms and Conditions
        st.subheader("Terms & Conditions")

        # Basic Terms
        col_terms1, col_terms2 = st.columns(2)
        with col_terms1:
            gst_percent = st.number_input("Taxes (%)",
                                          min_value=0.0,
                                          value=18.0,
                                          step=0.1)
            payment_options = [
                "100% Against PI", "50% Advance Balance Against PI",
                "30% Advance Balance Against PI", "Custom"
            ]
            payment_choice = st.selectbox("Payment Terms", payment_options)
            if payment_choice == "Custom":
                payment_terms = st.text_input("Custom Payment Terms",
                                              value="100% Against PI")
            else:
                payment_terms = payment_choice

        with col_terms2:
            price_terms = st.text_input("Price", value="Ex-works, Mumbai")
            freight_terms = st.text_input("Freight & Transit Insurance",
                                          value="In your scope")

        additional_terms = st.text_area(
            "Additional Terms and Conditions",
            value=
            "Packing: 2% Extra.\nInstallation & Commissioning charges not included."
        )

        st.divider()

        # Get extended terms from session state for PDF generation
        warranty_terms = st.session_state.get(
            'company_warranty',
            "Period shall be within 12 months from the date of commissioning or 18 months from the date of supply whichever is earlier. Warranty is not applicable for spare parts."
        )

        cancellation_terms = st.session_state.get(
            'company_cancellation',
            "In case of cancellation of order after 7 days of PO placement, cancellation charges would be applicable at the rate of 20% for standard valves and 40% for Non Standard valves on the order value."
        )

        penalty_terms = st.session_state.get(
            'company_penalty',
            "In case of Non lifting of consignment after the contractual delivery date, we reserve the right to charge penalty at the rate of 5% per month on order value."
        )

    with col2:
        # Preview Section
        st.subheader("Quotation Preview")

        if st.session_state.current_line_items:
            # Calculate totals
            totals = calculate_totals(st.session_state.current_line_items, 0,
                                      gst_percent)

            # Display summary
            st.metric("Subtotal", f"₹{totals['subtotal']:,.2f}")
            st.metric("Taxable Amount", f"₹{totals['taxable_amount']:,.2f}")
            st.metric("GST", f"₹{totals['gst_amount']:,.2f}")
            st.metric("**Total Amount**", f"₹{totals['total_amount']:,.2f}")

            # Generate PDF button
            if st.button("Generate PDF",
                         type="primary",
                         use_container_width=True):
                if client_name and quote_ref:
                    quotation_data = {
                        'quote_ref':
                        quote_ref,
                        'quote_date':
                        quote_date.strftime('%d-%b-%Y'),
                        'validity_date':
                        (quote_date +
                         timedelta(days=validity_days)).strftime('%d-%b-%Y'),
                        'company': {
                            'name':
                            st.session_state.get('company_name',
                                                 'MACHT AUTOMATION LLP'),
                            'address':
                            st.session_state.get(
                                'company_address',
                                'Off 01, Grd Floor, Laxmi Niwas, Ram Maruti Road, Naupada, Thane (W) Thane 400602, Maharashtra, India.'
                            ),
                            'email':
                            st.session_state.get('company_email',
                                                 'sales@macht-automation.com'),
                            'phone':
                            st.session_state.get('company_phone',
                                                 '9820667352 / 9167930569'),
                            'gst':
                            st.session_state.get('company_gst',
                                                 '27ABRFM7709G1ZR'),
                            'msme':
                            st.session_state.get('company_msme',
                                                 'UDYAM-MH-33-0133361')
                        },
                        'client': {
                            'name': client_name,
                            'address': client_address,
                            'email': client_email,
                            'phone': client_phone,
                            'contact_person': client_contact_person
                        },
                        'subject':
                        subject,
                        'line_items':
                        st.session_state.current_line_items,
                        'totals':
                        totals,
                        'terms': {
                            'payment': payment_terms,
                            'price': price_terms,
                            'freight': freight_terms,
                            'warranty': warranty_terms,
                            'cancellation': cancellation_terms,
                            'penalty': penalty_terms,
                            'additional': additional_terms
                        }
                    }

                    # Generate PDF
                    pdf_buffer = generate_quotation_pdf(quotation_data)

                    # Save quotation
                    save_quotation(quotation_data)

                    # Download button
                    st.download_button(label="Download PDF",
                                       data=pdf_buffer,
                                       file_name=f"Quotation_{quote_ref}.pdf",
                                       mime="application/pdf",
                                       type="primary")

                    st.success("Quotation generated successfully!")
                else:
                    st.error(
                        "Please fill in Customer Name and Quote Reference.")
        else:
            st.info("Add line items to see preview and generate PDF.")

elif page == "Manage Quotations":
    st.header("Manage Quotations")

    quotations = get_quotations()

    if quotations:
        st.subheader(f"Total Quotations: {len(quotations)}")

        # Display quotations in a table
        quotation_data = []
        for quote in quotations:
            quotation_data.append({
                'Quote Ref': quote['quote_ref'],
                'Date': quote['quote_date'],
                'Customer': quote['client']['name'],
                'Total Amount': f"₹{quote['totals']['total_amount']:,.2f}",
                'Items': len(quote['line_items'])
            })

        df = pd.DataFrame(quotation_data)
        st.dataframe(df, use_container_width=True)

        # Option to regenerate PDF for existing quotations
        st.subheader("Regenerate PDF")
        selected_quote_ref = st.selectbox("Select Quotation",
                                          [q['quote_ref'] for q in quotations])

        if st.button("Regenerate PDF"):
            selected_quotation = next(
                (q
                 for q in quotations if q['quote_ref'] == selected_quote_ref),
                None)
            if selected_quotation:
                pdf_buffer = generate_quotation_pdf(selected_quotation)
                st.download_button(
                    label="Download PDF",
                    data=pdf_buffer,
                    file_name=f"Quotation_{selected_quote_ref}.pdf",
                    mime="application/pdf",
                    type="primary")
    else:
        st.info("No quotations found. Create your first quotation!")

    # Clear all quotations button
    if st.button("Clear All Quotations", type="secondary"):
        st.session_state.quotations = []
        st.success("All quotations cleared!")
        st.rerun()

elif page == "Configuration":
    st.header("Company Configuration")

    # Company Information Section
    st.subheader("Company Information")

    col_config1, col_config2 = st.columns(2)

    with col_config1:
        # Company Logo Section
        st.subheader("Company Logo")
        company_logo = st.file_uploader("Upload Company Logo",
                                        type=['png', 'jpg', 'jpeg'])
        if company_logo:
            st.image(company_logo, width=200)
            st.session_state.company_logo = company_logo

        # Basic Company Info
        company_name = st.text_input("Company Name",
                                     value=st.session_state.get(
                                         'company_name', 'DEVSHRI MARKETING'))
        company_address = st.text_area(
            "Company Address",
            value=st.session_state.get(
                'company_address',
                '2/49, Suraj Building, J. B. Marg, Elphinstone Road, Prabhadevi, Mumbai - 400013.'
            ))
        company_email = st.text_input("Company Email",
                                      value=st.session_state.get(
                                          'company_email',
                                          'sales@devshrimarketing.com.com'))

    with col_config2:
        st.subheader("Contact & Registration")
        company_phone = st.text_input("Company Phone",
                                      value=st.session_state.get(
                                          'company_phone', '9821219871'))
        company_gst = st.text_input("GST Number",
                                    value=st.session_state.get(
                                        'company_gst', '27AAEFD3217G1ZS'))
        company_msme = st.text_input("MSME Number",
                                     value=st.session_state.get(
                                         'company_msme',
                                         'UDYAM-MH-19-0084808'))

    st.divider()

    # Terms & Conditions Configuration
    st.subheader("Default Terms & Conditions")

    warranty_terms = st.text_area(
        "Warranty Terms",
        value=st.session_state.get(
            'company_warranty',
            "Period shall be within 12 months from the date of commissioning or 18 months from the date of supply whichever is earlier. Warranty is not applicable for spare parts."
        ))

    cancellation_terms = st.text_area(
        "Cancellation Terms",
        value=st.session_state.get(
            'company_cancellation',
            "In case of cancellation of order after 7 days of PO placement, cancellation charges would be applicable at the rate of 20% for standard valves and 40% for Non Standard valves on the order value."
        ))

    penalty_terms = st.text_area(
        "Penalty Terms",
        value=st.session_state.get(
            'company_penalty',
            "In case of Non lifting of consignment after the contractual delivery date, we reserve the right to charge penalty at the rate of 5% per month on order value."
        ))

    # Save Configuration Button
    if st.button("Save Configuration", type="primary"):
        # Save all company information to session state
        st.session_state.company_name = company_name
        st.session_state.company_address = company_address
        st.session_state.company_email = company_email
        st.session_state.company_phone = company_phone
        st.session_state.company_gst = company_gst
        st.session_state.company_msme = company_msme
        st.session_state.company_warranty = warranty_terms
        st.session_state.company_cancellation = cancellation_terms
        st.session_state.company_penalty = penalty_terms

        st.success("Configuration saved successfully!")
        st.rerun()

    # Display current configuration status
    st.divider()
    st.subheader("Current Configuration Status")

    config_status = {
        "Company Name":
        st.session_state.get('company_name', 'Not set'),
        "Company Email":
        st.session_state.get('company_email', 'Not set'),
        "Company Phone":
        st.session_state.get('company_phone', 'Not set'),
        "GST Number":
        st.session_state.get('company_gst', 'Not set'),
        "MSME Number":
        st.session_state.get('company_msme', 'Not set'),
        "Logo":
        "Uploaded" if st.session_state.get('company_logo') else "Not uploaded"
    }

    config_df = pd.DataFrame(list(config_status.items()),
                             columns=['Setting', 'Value'])
    st.dataframe(config_df, use_container_width=True)
