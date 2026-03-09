# Testing Checklist - Aqui Estoy! Web Application

## Pre-Testing Setup

- [ ] Database migrations applied: `python manage.py migrate`
- [ ] Tailwind CSS compiled: `npm run build:css`
- [ ] Development server running: `python manage.py runserver`
- [ ] At least one test user created
- [ ] Sample data in database (casos, categorias, etc.)

---

## Authentication Tests

### Login Page (`/web/login/`)
- [ ] Page loads with blue gradient background
- [ ] Email and password fields visible
- [ ] "Remember me" checkbox present
- [ ] "Register" link works
- [ ] Login with valid credentials succeeds
- [ ] Login with invalid credentials shows error
- [ ] JWT token stored in localStorage after login
- [ ] Redirect to home page after successful login
- [ ] Password visibility toggle works
- [ ] Form validation (required fields)

### Register Page (`/web/register/`)
- [ ] All fields present (nombres, apellidos, correo, teléfono, etc.)
- [ ] Email format validation works
- [ ] Phone number validation (10 digits)
- [ ] Password strength validation (min 8 chars)
- [ ] Password confirmation matches
- [ ] Tipo usuario dropdown populated
- [ ] Registration success redirects to login
- [ ] Error messages display correctly
- [ ] "Login" link works

---

## Dashboard Tests

### Home Page (`/web/home/`)
- [ ] Statistics cards display (casos activos, donaciones, etc.)
- [ ] Category grid displays all categories
- [ ] Featured cases grid displays
- [ ] Case cards show image, title, progress bar
- [ ] "Ver más" button on each case works
- [ ] User info in navbar displays correctly
- [ ] Avatar image displays
- [ ] Logout from dropdown works

---

## Case Management Tests

### Case Listing (`/web/casos/`)
- [ ] All cases display in grid layout
- [ ] Search bar filters by text
- [ ] Category filter works
- [ ] Estado filter works
- [ ] Pagination displays when >12 cases
- [ ] Previous/Next buttons work
- [ ] Case cards clickable to detail page
- [ ] Loading spinner shows during fetch
- [ ] Empty state shows when no results

### Case Detail (`/web/casos/<id>/`)
- [ ] Main case image displays
- [ ] Image gallery thumbnails display
- [ ] Clicking thumbnail changes main image
- [ ] Case title and description display
- [ ] Beneficiary info sidebar displays
- [ ] Progress bar shows correct percentage
- [ ] Monto recaudado vs meta shows correctly
- [ ] "Donar Ahora" button opens modal
- [ ] Donation modal has preset amounts
- [ ] Custom amount input works
- [ ] Similar cases section displays
- [ ] Share button functionality
- [ ] Report case button works

### Create Case (`/web/casos/crear/`)
- [ ] All form sections display
- [ ] Basic info fields work
- [ ] Location fields work
- [ ] Category dropdown populated
- [ ] Meta económica accepts numbers
- [ ] Image upload (4 images) works
- [ ] Image preview displays after selection
- [ ] File size validation (max 5MB)
- [ ] Form validation on submit
- [ ] Success message after creation
- [ ] Redirect to case detail after creation

---

## 👤 Profile Tests

### Profile Page (`/web/perfil/`)
- [ ] User avatar displays in sidebar
- [ ] User name and email display
- [ ] Statistics cards show correct numbers
- [ ] "Información" tab displays personal data
- [ ] All fields are editable
- [ ] Update profile button works
- [ ] Success message after update
- [ ] "Seguridad" tab displays password form
- [ ] Change password requires current password
- [ ] New password validation works
- [ ] Password confirmation matches
- [ ] Success message after password change
- [ ] "Actividad" tab displays
- [ ] My cases list displays
- [ ] My donations list displays
- [ ] Click on case/donation navigates correctly
- [ ] Avatar upload button works
- [ ] New avatar preview displays

---

## Donation Tests

### Donations List (`/web/donaciones/`)
- [ ] Statistics summary displays (total, count, average)
- [ ] All donations display
- [ ] Search bar filters by case name
- [ ] Estado filter works
- [ ] Date range filters work
- [ ] "Limpiar" button resets filters
- [ ] Pagination works correctly
- [ ] Click on donation opens detail modal
- [ ] Modal shows case info
- [ ] Modal shows payment method
- [ ] Modal shows receipt (if available)
- [ ] Empty state displays when no donations

### Create Donation (`/web/donaciones/crear/<caso_id>/`)
- [ ] Case preview displays at top
- [ ] Case progress bar shows
- [ ] Preset amount buttons ($100, $250, $500, $1000)
- [ ] Clicking preset amount fills input
- [ ] Custom amount input works
- [ ] Minimum amount validation ($10)
- [ ] Payment method selection works
- [ ] Optional message textarea works
- [ ] Anonymous checkbox works
- [ ] Terms checkbox required
- [ ] Summary sidebar updates with amount
- [ ] Security badge displays
- [ ] Tax deductible notice displays
- [ ] Submit button disabled during processing
- [ ] Success modal displays after donation
- [ ] Links in success modal work
- [ ] Auto-redirect after 5 seconds

---

##  Navigation Tests

### Main Navigation
- [ ] Logo links to home
- [ ] "Inicio" link works
- [ ] "Casos" link works
- [ ] "Mis Donaciones" link works
- [ ] "Crear Caso" button works
- [ ] User dropdown displays on click
- [ ] "Mi Perfil" link in dropdown works
- [ ] "Cerrar Sesión" link works
- [ ] Logout confirmation dialog appears
- [ ] Mobile menu button displays on small screens

### Footer
- [ ] Footer displays on all pages
- [ ] Footer links work
- [ ] Contact email displays

---

##  UI/UX Tests

### Visual Design
- [ ] Blue/white color scheme consistent
- [ ] All buttons have hover states
- [ ] Transitions smooth (0.3s)
- [ ] Shadows consistent (shadow-lg)
- [ ] Border radius consistent (rounded-lg)
- [ ] Typography hierarchy clear
- [ ] Icons display correctly (Heroicons)

### Responsive Design
- [ ] Desktop view (1920x1080) works
- [ ] Tablet view (768x1024) works
- [ ] Mobile view (375x667) works
- [ ] Grid layouts adapt to screen size
- [ ] Text sizes responsive
- [ ] Images scale properly
- [ ] Modals fit on small screens

### Interactions
- [ ] Loading spinners display during API calls
- [ ] Alert messages display correctly
- [ ] Success alerts are green
- [ ] Error alerts are red
- [ ] Warning alerts are yellow
- [ ] Info alerts are blue
- [ ] Alerts auto-dismiss after 5 seconds
- [ ] Modal close buttons work
- [ ] ESC key closes modals
- [ ] Click outside closes modals

---

## 🔌 API Integration Tests

### Authentication API
- [ ] POST `/api/auth/token/` returns access token
- [ ] POST `/api/auth/token/refresh/` refreshes token
- [ ] GET `/api/usuarios/me/` returns current user
- [ ] PATCH `/api/usuarios/me/perfil/` updates profile
- [ ] PATCH `/api/usuarios/me/contrasena/` changes password

### Cases API
- [ ] GET `/api/casos/` returns all cases
- [ ] GET `/api/casos/<id>/` returns specific case
- [ ] POST `/api/casos/` creates new case
- [ ] PATCH `/api/casos/<id>/` updates case
- [ ] DELETE `/api/casos/<id>/` deletes case
- [ ] GET `/api/casos/?beneficiario=<id>` filters by user

### Donations API
- [ ] GET `/api/donaciones/` returns all donations
- [ ] GET `/api/donaciones/<id>/` returns specific donation
- [ ] POST `/api/donaciones/` creates new donation
- [ ] GET `/api/donaciones/?donador=<id>` filters by donor
- [ ] GET `/api/donaciones/?caso=<id>` filters by case

### Categories API
- [ ] GET `/api/categorias/` returns all categories

---

##  Security Tests

- [ ] Unauthenticated users redirected to login
- [ ] JWT token required for protected endpoints
- [ ] Expired token triggers refresh
- [ ] Invalid token redirects to login
- [ ] CSRF token included in forms
- [ ] File upload validates file type
- [ ] File upload validates file size
- [ ] XSS protection in place
- [ ] SQL injection protection (ORM)

---

## 📱 Browser Compatibility

- [ ] Chrome/Edge (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Mobile Safari (iOS)
- [ ] Chrome Mobile (Android)

---

## ⚡ Performance Tests

- [ ] Page load time < 3 seconds
- [ ] API response time < 1 second
- [ ] Images optimized/compressed
- [ ] CSS/JS minified in production
- [ ] No console errors
- [ ] No console warnings (important)
- [ ] Network tab shows < 50 requests per page
- [ ] Lighthouse score > 80

---

##  Error Handling Tests

- [ ] Network error displays message
- [ ] 404 error handled gracefully
- [ ] 500 error shows generic message
- [ ] Form validation errors display
- [ ] File upload errors display
- [ ] Missing data shows placeholder
- [ ] Empty arrays show empty state
- [ ] Broken images show fallback

---

##  Data Validation Tests

### Registration
- [ ] Empty fields show error
- [ ] Invalid email format rejected
- [ ] Short password rejected
- [ ] Mismatched passwords rejected
- [ ] Invalid phone number rejected

### Case Creation
- [ ] Empty title rejected
- [ ] Empty description rejected
- [ ] Meta económica must be positive
- [ ] At least one category required
- [ ] At least one image required

### Donation
- [ ] Amount below $10 rejected
- [ ] No payment method selected rejected
- [ ] Terms not accepted rejected
- [ ] Invalid caso_id rejected

---

##  User Flow Tests

### Complete Registration → Donation Flow
1. [ ] Register new account
2. [ ] Verify email sent (if enabled)
3. [ ] Login with new account
4. [ ] Browse cases
5. [ ] View case detail
6. [ ] Make donation
7. [ ] View donation in "Mis Donaciones"
8. [ ] Update profile
9. [ ] Logout

### Complete Case Creation Flow
1. [ ] Login
2. [ ] Click "Crear Caso"
3. [ ] Fill all form fields
4. [ ] Upload images
5. [ ] Submit form
6. [ ] View created case
7. [ ] Verify case in "Mis Casos"
8. [ ] Edit case (if allowed)

---

## ✅ Final Checklist

- [ ] All pages tested
- [ ] All forms tested
- [ ] All API endpoints tested
- [ ] All user flows tested
- [ ] No critical bugs found
- [ ] Documentation complete
- [ ] Code commented
- [ ] README updated

---

## 📝 Bug Report Template

```
**Bug Title:** 
**Page/Component:** 
**Steps to Reproduce:**
1. 
2. 
3. 

**Expected Behavior:** 
**Actual Behavior:** 
**Browser:** 
**Screenshots:** 
**Console Errors:** 
```

---

##  Deployment Checklist

- [ ] Environment variables configured
- [ ] Database migrations run
- [ ] Static files collected
- [ ] Media files directory set up
- [ ] ALLOWED_HOSTS configured
- [ ] DEBUG = False
- [ ] SECRET_KEY changed
- [ ] HTTPS enabled
- [ ] Backup strategy in place
- [ ] Monitoring set up
- [ ] Error logging configured

---

**Testing Status:**  Pending  
**Last Updated:** 2026-01-XX  
**Tested By:** _________________
