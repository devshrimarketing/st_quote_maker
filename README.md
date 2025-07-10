# Quotation Generator - Streamlit Application

## Overview

This is a professional quotation generator built with Streamlit that allows users to create, manage, and generate PDF quotations for businesses. The application is specifically configured for "MACHT AUTOMATION LLP" but can be customized for other companies. It features a clean web interface for creating quotations with line items, item-wise discount calculations, calculating totals with GST, and generating professional PDF documents with a structured business layout. The application includes date validation to prevent future-dated quotations and allows only current or back-dated quotations up to 25 days.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web framework
- **Layout**: Wide layout with multi-column design
- **Navigation**: Sidebar-based radio navigation between "Create Quotation", "Manage Quotations", and "Configuration" pages
- **State Management**: Session-based state management using Streamlit's built-in session state for quotations and company configuration
- **Configuration Management**: Separate configuration page for company information, logo, and default terms

### Backend Architecture
- **Language**: Python
- **Architecture Pattern**: Modular utility-based architecture
- **Data Storage**: In-memory session state (temporary storage)
- **PDF Generation**: ReportLab library for creating professional PDF documents

## Key Components

### 1. Main Application (app.py)
- **Purpose**: Main entry point and UI controller
- **Features**: 
  - Three-page navigation (Create Quotation, Manage Quotations, Configuration)
  - Customer information input (renamed from client)
  - Line item management with delivery weeks and item-wise discounts
  - Company configuration management
  - Terms and conditions integration
- **Design**: Two-column layout for better organization with radio-based sidebar navigation

### 2. Data Management (data/quotations.py)
- **Purpose**: Handle quotation data operations and company configuration
- **Features**:
  - Session state initialization for quotations and company settings
  - CRUD operations for quotations
  - JSON export/import functionality
  - Timestamp tracking for quotations
  - Company configuration initialization with default values
  - Persistent storage of company information, warranty, cancellation, and penalty terms

### 3. Calculations Module (utils/calculations.py)
- **Purpose**: Handle all financial calculations
- **Features**:
  - Subtotal calculations (sum of individual item totals after item-wise discounts)
  - Item-wise discount calculations (percentage-based per item)
  - Additional discount calculations (percentage-based on total)
  - GST calculations (default 18%)
  - Currency formatting (Indian Rupee format)
  - Line item total calculations with individual discount support

### 4. PDF Generation (utils/pdf_generator.py)
- **Purpose**: Generate professional PDF quotations
- **Features**:
  - Professional document layout with structured header (company info top-right, logo support top-left)
  - Reduced margins (0.5 inch) for better content utilization
  - Logo embedding support from uploaded company logos
  - Centered quotation title with bold formatting
  - Complete customer information display (address, email, contact person)
  - Reformatted item table with wrapped headers to prevent overflow
  - Multi-page table support with repeating headers
  - Right-aligned numeric columns (quantity, rate, total) for better readability
  - Item-wise discount support with proper formatting
  - Quantity display with UOM (No/Nos)
  - Date validation (current or back-dated up to 25 days only)
  - Improved signature block formatting
  - Color-coded headers with no background color for data rows
  - A4 page size with optimized column widths

## Data Flow

1. **User Input**: User enters company and client information through Streamlit forms
2. **Line Item Management**: Items are added to session state for temporary storage
3. **Calculations**: Financial calculations are performed in real-time using the calculations module
4. **PDF Generation**: When requested, data is passed to PDF generator for document creation
5. **Storage**: Quotations are stored in session state (temporary, lost on session end)

## External Dependencies

### Core Libraries
- **Streamlit**: Web application framework
- **Pandas**: Data manipulation (imported but usage not shown in provided code)
- **ReportLab**: PDF generation library
- **DateTime**: Date and time handling

### PDF Generation Dependencies
- ReportLab components:
  - `SimpleDocTemplate` for document structure
  - `Table` and `TableStyle` for tabular data
  - `Paragraph` and custom styles for text formatting
  - Color management for professional appearance

## Deployment Strategy

### Current Setup
- **Environment**: Designed for Streamlit deployment
- **Data Persistence**: Session-based (temporary storage)
- **Configuration**: Single-page application with embedded company details

### Recommended Improvements
1. **Database Integration**: Add persistent storage (PostgreSQL recommended)
2. **User Authentication**: Multi-company support with user management
3. **File Storage**: Cloud storage for PDF documents
4. **Environment Variables**: Externalize company configuration
5. **Backup System**: Regular data backup and recovery mechanisms

### Deployment Considerations
- The application currently uses session state for data storage, which means data is lost when the session ends
- For production use, consider implementing database storage
- PDF generation creates documents in memory using BytesIO buffers
- The application is pre-configured for a specific company but can be made configurable

## Technical Notes

- **GST Rate**: Hardcoded to 18% (Indian standard rate)
- **Currency**: Indian Rupee (₹) formatting
- **PDF Format**: A4 size with professional business document styling
- **State Management**: Streamlit session state used for temporary data persistence
- **Error Handling**: Basic error handling present in JSON import/export functions