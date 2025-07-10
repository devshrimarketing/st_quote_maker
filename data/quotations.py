import streamlit as st
import json
from datetime import datetime

def init_session_state():
    """Initialize session state for quotations"""
    if 'quotations' not in st.session_state:
        st.session_state.quotations = []
    
    if 'current_line_items' not in st.session_state:
        st.session_state.current_line_items = []
    
    # Initialize company configuration with defaults
    if 'company_name' not in st.session_state:
        st.session_state.company_name = 'MACHT AUTOMATION LLP'
    if 'company_address' not in st.session_state:
        st.session_state.company_address = 'Off 01, Grd Floor, Laxmi Niwas, Ram Maruti Road, Naupada, Thane (W) Thane 400602, Maharashtra, India.'
    if 'company_email' not in st.session_state:
        st.session_state.company_email = 'sales@macht-automation.com'
    if 'company_phone' not in st.session_state:
        st.session_state.company_phone = '9820667352 / 9167930569'
    if 'company_gst' not in st.session_state:
        st.session_state.company_gst = '27ABRFM7709G1ZR'
    if 'company_msme' not in st.session_state:
        st.session_state.company_msme = 'UDYAM-MH-33-0133361'
    if 'company_warranty' not in st.session_state:
        st.session_state.company_warranty = 'Period shall be within 12 months from the date of commissioning or 18 months from the date of supply whichever is earlier. Warranty is not applicable for spare parts.'
    if 'company_cancellation' not in st.session_state:
        st.session_state.company_cancellation = 'In case of cancellation of order after 7 days of PO placement, cancellation charges would be applicable at the rate of 20% for standard valves and 40% for Non Standard valves on the order value.'
    if 'company_penalty' not in st.session_state:
        st.session_state.company_penalty = 'In case of Non lifting of consignment after the contractual delivery date, we reserve the right to charge penalty at the rate of 5% per month on order value.'

def save_quotation(quotation_data):
    """Save quotation to session state"""
    # Add timestamp
    quotation_data['created_at'] = datetime.now().isoformat()
    
    # Add to session state
    st.session_state.quotations.append(quotation_data)
    
    # Clear current line items after saving
    st.session_state.current_line_items = []

def get_quotations():
    """Get all quotations from session state"""
    return st.session_state.quotations

def get_quotation_by_ref(quote_ref):
    """Get specific quotation by reference"""
    for quotation in st.session_state.quotations:
        if quotation['quote_ref'] == quote_ref:
            return quotation
    return None

def delete_quotation(quote_ref):
    """Delete quotation by reference"""
    st.session_state.quotations = [
        q for q in st.session_state.quotations 
        if q['quote_ref'] != quote_ref
    ]

def export_quotations_json():
    """Export all quotations as JSON"""
    return json.dumps(st.session_state.quotations, indent=2, default=str)

def import_quotations_json(json_data):
    """Import quotations from JSON"""
    try:
        quotations = json.loads(json_data)
        st.session_state.quotations = quotations
        return True
    except json.JSONDecodeError:
        return False

def get_next_quote_number():
    """Generate next quote reference number"""
    today = datetime.now()
    date_str = today.strftime('%Y%m%d')
    
    # Count existing quotations for today
    today_quotes = [
        q for q in st.session_state.quotations 
        if q['quote_ref'].startswith(f'Q{date_str}')
    ]
    
    next_number = len(today_quotes) + 1
    return f'Q{date_str}{next_number:03d}'
