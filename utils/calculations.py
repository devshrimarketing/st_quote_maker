def calculate_totals(line_items, discount_percent=0, gst_percent=18):
    """Calculate totals for quotation including discount and GST"""
    
    # Calculate subtotal (sum of all item totals after individual discounts)
    subtotal = sum(item['total_price'] for item in line_items)
    
    # Calculate additional discount on subtotal if specified
    additional_discount_amount = subtotal * (discount_percent / 100)
    
    # Calculate taxable amount after additional discount
    taxable_amount = subtotal - additional_discount_amount
    
    # Calculate GST
    gst_amount = taxable_amount * (gst_percent / 100)
    
    # Calculate total amount
    total_amount = taxable_amount + gst_amount
    
    # Calculate total discount including item-wise discounts
    total_item_discounts = sum(item.get('discount_amount', 0) for item in line_items)
    total_discount_amount = total_item_discounts + additional_discount_amount
    
    return {
        'subtotal': subtotal,
        'discount_percent': discount_percent,
        'discount_amount': additional_discount_amount,
        'total_discount_amount': total_discount_amount,
        'taxable_amount': taxable_amount,
        'gst_percent': gst_percent,
        'gst_amount': gst_amount,
        'total_amount': total_amount
    }

def format_currency(amount):
    """Format currency in Indian format"""
    return f"₹{amount:,.2f}"

def calculate_line_total(quantity, unit_price):
    """Calculate total for a single line item"""
    return quantity * unit_price
