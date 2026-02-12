# Donations Project

## Overview
The Donations Project is a Django web application designed to facilitate donations to various causes. It provides a user-friendly interface for managing cases, users, donations, and categories.

## Features
- User profiles with personal information
- Listing of recent cases and case history
- Management of donations and categories
- Admin interface for managing users and cases

## Project Structure
```
donations_project/
├── manage.py               # Command-line utility for interacting with the project
├── requirements.txt        # Project dependencies
├── .env.example            # Template for environment variables
├── donations_project/
│   ├── __init__.py        # Indicates that this directory is a Python package
│   ├── settings.py         # Project settings and configuration
│   ├── urls.py             # URL patterns for the project
│   ├── wsgi.py             # WSGI entry point for deployment
│   └── asgi.py             # ASGI entry point for asynchronous deployment
├── members/
│   ├── __init__.py        # Indicates that this directory is a Python package
│   ├── admin.py            # Admin site configuration
│   ├── apps.py             # App configuration
│   ├── models.py           # Data models for the application
│   ├── views.py            # View functions for handling requests
│   ├── urls.py             # URL patterns for the members app
│   ├── forms.py            # Forms for user input
│   ├── serializers.py       # Serializers for data conversion
│   ├── tests.py            # Test cases for the application
│   ├── migrations/         # Database migrations
│   │   └── __init__.py     # Indicates that this directory is a Python package
│   ├── templates/          # HTML templates for rendering views
│   │   └── members/
│   │       ├── base.html
│   │       ├── feed.html
│   │       ├── lista_casos.html
│   │       ├── detalle_caso.html
│   │       ├── lista_usuarios.html
│   │       ├── perfil_usuario.html
│   │       ├── lista_donaciones.html
│   │       └── lista_categorias.html
│   └── static/             # Static files (CSS, JS)
│       └── members/
│           ├── css/
│           │   └── styles.css
│           └── js/
│               └── feed.js
└── README.md               # Project documentation
```

## Installation
1. Clone the repository:
   ```
   git clone <repository-url>
   cd donations_project
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   - Copy `.env.example` to `.env` and fill in the necessary values.

5. Run migrations:
   ```
   python manage.py migrate
   ```

6. Create a superuser (optional):
   ```
   python manage.py createsuperuser
   ```

7. Start the development server:
   ```
   python manage.py runserver
   ```

## Usage
- Access the application at `http://127.0.0.1:8000/`.
- Use the admin interface at `http://127.0.0.1:8000/admin/` to manage users and cases.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.