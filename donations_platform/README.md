# Donations Platform

This project is a Django-based web application designed to facilitate donations and communication between donors and beneficiaries. It includes user authentication, role-based access control, and features for managing donations and cases.

## Features

- User registration and login functionality
- Role-based access control for managing permissions
- Intermediary user model for handling donations and communication
- Management of cases and donations
- Messaging system for communication between users

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd donations_platform
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
   - Copy `.env.example` to `.env` and fill in the necessary configurations.

5. Run migrations:
   ```
   python manage.py migrate
   ```

6. Create a superuser (optional):
   ```
   python manage.py createsuperuser
   ```

7. Run the development server:
   ```
   python manage.py runserver
   ```

## Usage

- Access the application at `http://127.0.0.1:8000/`
- Use the provided templates for user registration, login, and profile management.
- Explore the donations and messaging features.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.