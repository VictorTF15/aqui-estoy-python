# Aqui Estoy! - Web Application Documentation
## User Interface Components - Completed

### Project Overview
**Name:** Aqui Estoy!  
**Description:** Social support platform connecting people in need with donors  
**Technology Stack:** Django 6.0.1, PostgreSQL, Tailwind CSS, Alpine.js, REST API  
**Color Scheme:** Blues (#0ea5e9, #0284c7, #075985) and white

---

##  Completed Components

### 1. **Authentication System**
-  **Login Page** (`members/templates/web/login.html`)
  - Email/password authentication
  - JWT token management
  - Remember me option
  - Blue gradient background with white form card
  - JavaScript: `members/static/js/web/login.js`

- ✅ **Register Page** (`members/templates/web/register.html`)
  - Complete user registration form
  - Fields: nombres, apellidos, correo, teléfono, ciudad, estado, tipo_usuario, contraseña
  - Form validation (email format, phone 10 digits, password min 8 chars)
  - JavaScript: `members/static/js/web/register.js`

### 2. **Dashboard & Home**
- ✅ **Home/Dashboard** (`members/templates/web/home.html`)
  - Statistics cards (casos activos, mis donaciones, mis casos, total donado)
  - Category filtering
  - Featured cases grid
  - Responsive layout
  - JavaScript: `members/static/js/web/home.js`

### 3. **Case Management**
- ✅ **Case Listing** (`members/templates/web/casos/lista.html`)
  - Grid layout with case cards
  - Search by text
  - Filter by category and estado
  - Pagination (prev/next)
  - JavaScript: `members/static/js/web/casos-lista.js`

- ✅ **Case Detail** (`members/templates/web/casos/detalle.html`)
  - Image gallery with main and thumbnails
  - Case description and updates
  - Progress bar (monto recaudado vs meta)
  - Beneficiary information sidebar
  - Donation modal with preset amounts ($50, $100, $250, $500, Custom)
  - Share functionality
  - Report case option
  - Similar cases section
  - JavaScript: `members/static/js/web/caso-detalle.js`

- ✅ **Create Case** (`members/templates/web/casos/crear.html`)
  - Multi-section form (Basic Info, Location, Category/Meta, Images)
  - Image upload with preview (4 images max)
  - FormData for file submission
  - JavaScript: `members/static/js/web/crear-caso.js`

### 4. **User Profile**
- ✅ **Profile Page** (`members/templates/web/perfil.html`)
  - Tabbed interface (Información, Seguridad, Actividad)
  - Editable personal information
  - Password change section
  - Avatar upload with preview
  - Statistics cards (mis casos, mis donaciones)
  - Activity feed (my cases, my donations)
  - JavaScript: `members/static/js/web/perfil.js`

### 5. **Donations**
- ✅ **Donations List** (`members/templates/web/donaciones/lista.html`)
  - Statistics summary (total donado, donaciones, casos apoyados, promedio)
  - Search and filters (estado, fecha desde/hasta)
  - Donation cards with case info
  - Pagination
  - Detail modal with case info, receipt, payment method
  - JavaScript: `members/static/js/web/lista-donaciones.js`

- ✅ **Create Donation** (`members/templates/web/donaciones/crear.html`)
  - Case information preview
  - Preset amount buttons ($100, $250, $500, $1000)
  - Custom amount input (min $10)
  - Payment method selection (Tarjeta, PayPal, Transferencia)
  - Optional support message
  - Anonymous donation checkbox
  - Terms acceptance
  - Summary sidebar with secure payment badges
  - Success confirmation modal
  - JavaScript: `members/static/js/web/crear-donacion.js`

---

## 📁 File Structure

```
members/
├── templates/
│   └── web/
│       ├── base_web.html          # Base template with nav & footer
│       ├── login.html              # Login page
│       ├── register.html           # Registration page
│       ├── home.html               # Dashboard
│       ├── perfil.html             # User profile
│       ├── casos/
│       │   ├── lista.html          # Case listing
│       │   ├── detalle.html        # Case detail
│       │   └── crear.html          # Create case
│       └── donaciones/
│           ├── lista.html          # Donations list
│           └── crear.html          # Create donation
│
├── static/
│   └── js/
│       ├── api/
│       │   ├── apiClient.js        # Base API client
│       │   └── authService.js      # Authentication service
│       └── web/
│           ├── login.js
│           ├── register.js
│           ├── home.js
│           ├── casos-lista.js
│           ├── caso-detalle.js
│           ├── crear-caso.js
│           ├── perfil.js
│           ├── lista-donaciones.js
│           └── crear-donacion.js
│
├── views/
│   └── web_views.py               # View functions for web routes
│
├── urls.py                        # URL routing
├── api_views.py                   # REST API ViewSets
└── serializers.py                 # DRF Serializers
```

---

## 🔗 URL Routes

```python
# WEB - Normal Users
path('web/login/', web_views.login_view, name='login_web'),
path('web/register/', web_views.register_view, name='register_web'),
path('web/home/', web_views.home_web, name='home_web'),
path('web/perfil/', web_views.perfil_web, name='perfil_web'),
path('web/casos/', web_views.lista_casos_web, name='lista_casos_web'),
path('web/casos/<int:id>/', web_views.detalle_caso_web, name='detalle_caso_web'),
path('web/casos/crear/', web_views.crear_caso_web, name='crear_caso_web'),
path('web/donaciones/', web_views.lista_donaciones_web, name='lista_donaciones_web'),
path('web/donaciones/crear/<int:caso_id>/', web_views.crear_donacion_web, name='crear_donacion_web'),
```

---

## 🎨 Design System

### Colors
- **Primary Sky:** `#0ea5e9` (sky-500)
- **Primary Blue:** `#0284c7` (sky-600)
- **Dark Blue:** `#075985` (sky-700)
- **Light Blue:** `#e0f2fe` (sky-50)
- **White:** `#ffffff`

### Components
- **Cards:** White background, rounded-lg, shadow-lg, border-sky-100
- **Buttons Primary:** bg-sky-600, hover:bg-sky-700, text-white
- **Buttons Secondary:** border-sky-300, text-sky-700, hover:bg-sky-50
- **Inputs:** border-sky-200, focus:ring-sky-500
- **Gradients:** from-sky-500 to-blue-600
- **Badges:** bg-sky-100 text-sky-800 (or status colors)

### Typography
- **Headings:** text-sky-800, font-bold
- **Body:** text-sky-600/text-sky-700
- **Links:** text-sky-600, hover:text-sky-700

---

## 🔐 Authentication Flow

1. User logs in at `/web/login/`
2. JWT access token stored in `localStorage.access_token`
3. Refresh token stored in `localStorage.refresh_token`
4. All API requests include `Authorization: Bearer {token}` header
5. `authService.getProfile()` retrieves user data
6. Base template checks authentication and loads user info
7. Logout clears tokens and redirects to login

---

## 📡 API Integration

### Base Client (`apiClient.js`)
- `get(endpoint)` - GET requests
- `post(endpoint, data)` - POST requests
- `put(endpoint, data)` - PUT requests
- `patch(endpoint, data)` - PATCH requests
- `delete(endpoint)` - DELETE requests
- `uploadFile(endpoint, formData)` - File uploads

### Auth Service (`authService.js`)
- `login(email, password)` - User login
- `register(userData)` - User registration
- `logout()` - Clear session
- `getProfile()` - Get current user
- `updateProfile(userData)` - Update user data
- `changePassword(current, new, confirm)` - Change password
- `refreshToken()` - Refresh JWT token

---

## ✨ Key Features

### User Experience
- ✅ Responsive design (mobile, tablet, desktop)
- ✅ Loading spinners during API calls
- ✅ Error handling with alert messages
- ✅ Form validation
- ✅ Image preview before upload
- ✅ Pagination for lists
- ✅ Search and filtering
- ✅ Modal dialogs
- ✅ Smooth transitions and animations

### Security
- ✅ JWT token authentication
- ✅ Protected routes (redirect to login if not authenticated)
- ✅ CSRF protection (Django)
- ✅ Password strength validation
- ✅ Secure file uploads

### Accessibility
- ✅ Semantic HTML
- ✅ Alt text for images
- ✅ Keyboard navigation support
- ✅ Focus states on interactive elements
- ✅ ARIA labels where needed

---

## 🚀 Getting Started

### Prerequisites
```bash
# Install dependencies
pip install -r requirements.txt
npm install
```

### Running the Application
```bash
# Compile Tailwind CSS
npm run build:css

# Run Django development server
python manage.py runserver
```

### Access Points
- **User Login:** http://localhost:8000/web/login/
- **User Register:** http://localhost:8000/web/register/
- **User Dashboard:** http://localhost:8000/web/home/
- **API Documentation:** http://localhost:8000/api/docs/
- **Admin Panel:** http://localhost:8000/admin/

---

## 📊 Database Models

- **Usuarios** - User accounts
- **Casos** - Support cases
- **Donaciones** - Donations
- **Categorias** - Case categories
- **EstadoCaso** - Case status (Pendiente, En progreso, Completado)
- **Conversaciones** - Chat conversations
- **Mensajes** - Messages
- **Reportes** - User reports
- **Sanciones** - User sanctions
- **DocumentosOCR** - OCR documents

---

## 🎯 Next Steps (Optional Enhancements)

- [ ] Email verification
- [ ] Password reset functionality
- [ ] Real-time notifications (WebSocket)
- [ ] Chat system between donors and beneficiaries
- [ ] Advanced analytics dashboard
- [ ] Export donations to PDF/Excel
- [ ] Social media sharing integration
- [ ] Multi-language support (i18n)
- [ ] Payment gateway integration (Stripe, PayPal)
- [ ] Mobile app (React Native / Flutter)

---

## 📝 Notes

- All components follow the blue/white color scheme
- JavaScript uses async/await for API calls
- Forms have client-side and server-side validation
- Images are uploaded to `/media/` directory
- API responses are in JSON format
- All dates are formatted in Spanish (es-ES)

---

**Project Status:** ✅ **Web Interface Complete**  
**Date:** 2026-01-XX  
**Version:** 1.0.0
