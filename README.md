# AURA Jewellery — Premium E-commerce & IMS Platform

A comprehensive, state-of-the-art solution for luxury jewellery businesses. AURA combines a high-end, visual-first storefront with a robust, enterprise-grade Inventory Management System (IMS).

## 💎 Project Overview

AURA is designed to bridge the gap between premium customer experiences and efficient back-office logistics. Built with **Django 5.1**, **Tailwind CSS v4**, **HTMX**, and **AlpineJS**, it offers a lightning-fast, reactive interface without the complexity of a heavy SPA.

### Key Features

#### Premium Storefront
- **Visual Excellence**: Modern, minimal design with glassmorphism and smooth micro-animations.
- **Dual Pricing Engine**: Automatic switching between **Retail** and **Verified Wholesale** pricing.
- **Interactive Product Gallery**: High-fidelity image zoom and seamless variation switching.
- **Dynamic Search & Filtering**: Instant discovery powered by HTMX partials.

#### IMS Suite (Admin Dashboard)
- **Live Inventory Tracking**: Real-time stock levels with low-stock automated alerts.
- **Unified Logistics**: Integrated shipping management with tracking number generation.
- **Omnichannel Sales**: Managed Online Orders alongside a dedicated **Point of Sale (POS)** terminal.
- **Vendor & PO Management**: Full lifecycle tracking for procurement and supplier relationships.

#### Administrative Oversight
- **Activity History (Audit Trail)**: Detailed logging of every administrative Create, Update, and Delete action.
- **Staff Management**: Role-based access control (RBAC) across five distinct user tiers.
- **Reporting Suite**: Deep insights with Sales, Inventory Valuation, and Customer performance reports.

#### Customer Engagement
- **Stockpile Management**: A unique "layaway" system allowing customers to store purchased items with automated fee calculation.
- **Product Reviews**: Star-rating system with administrative moderation workflow.
- **Wishlist & Cart**: Persistent, session-aware shopping tools.

## Tech Stack

- **Backend**: Django 5.1 (Active Python 3.12+)
- **Styling**: Tailwind CSS v4 (AURA Palette: Gold/Black/White)
- **Interactivity**: AlpineJS (State) & HTMX (Reactive Server Comms)
- **Email**: Django SMTP (Transaction-ready templates)
- **Database**: PostgreSQL (Recommended for production) / SQLite (Dev)

## 🚀 Getting Started

### 1. Prerequisites
Ensure you have Python 3.12+ installed on your system.

### 2. Setup (Windows)
```bash
# Clone and enter the project
git clone https://github.com/dimejiwebtech/Ecommerce-Inventory-System.git
cd Ecommerce-Inventory-System

# Initialize Virtual Environment
python -m venv venv
venv\Scripts\activate

# Install Dependencies
pip install -r requirements.txt
```

### 3. Database Initialization
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 4. Run Development Server
```bash
python manage.py runserver
```

## Deployment

The platform is configured for deployment on **Vercel** or traditional VPS providers via Gunicorn/WhiteNoise.

---

*AURA Jewellery — Elevating the standard for luxury retail technology.*
