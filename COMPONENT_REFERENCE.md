# Aqui Estoy! - Quick Component Reference

## 🎨 Reusable UI Components

### 1. Alert Messages
```javascript
showAlert(message, type = 'danger') {
    // Types: 'success', 'danger', 'warning', 'info'
    // Auto-dismiss after 5 seconds
}
```

**Usage:**
```javascript
showAlert('Operación exitosa', 'success');
showAlert('Error al procesar', 'danger');
showAlert('Por favor verifica', 'warning');
showAlert('Información adicional', 'info');
```

---

### 2. Loading Spinner
```html
<div id="loadingSpinner" class="flex justify-center items-center p-12">
    <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-sky-600"></div>
</div>
```

**Control:**
```javascript
document.getElementById('loadingSpinner').classList.add('hidden');
document.getElementById('loadingSpinner').classList.remove('hidden');
```

---

### 3. Modal Dialog
```html
<div id="myModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 hidden items-center justify-center p-4">
    <div class="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6 border-b border-sky-100 flex justify-between items-center">
            <h3 class="text-xl font-semibold text-sky-800">Modal Title</h3>
            <button onclick="closeModal()" class="text-sky-400 hover:text-sky-600">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
            </button>
        </div>
        <div class="p-6">
            <!-- Modal Content -->
        </div>
    </div>
</div>
```

**Functions:**
```javascript
function openModal() {
    document.getElementById('myModal').classList.remove('hidden');
    document.getElementById('myModal').classList.add('flex');
}

function closeModal() {
    document.getElementById('myModal').classList.add('hidden');
    document.getElementById('myModal').classList.remove('flex');
}

// Close on ESC key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') closeModal();
});

// Close on click outside
document.getElementById('myModal').addEventListener('click', function(e) {
    if (e.target === this) closeModal();
});
```

---

### 4. Card Component
```html
<div class="bg-white rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition">
    <img src="image.jpg" alt="Image" class="w-full h-48 object-cover">
    <div class="p-6">
        <h3 class="text-xl font-semibold text-sky-800 mb-2">Card Title</h3>
        <p class="text-sky-600 mb-4">Card description text</p>
        <button class="w-full px-4 py-2 bg-sky-600 text-white rounded-lg hover:bg-sky-700">
            Action Button
        </button>
    </div>
</div>
```

---

### 5. Form Input
```html
<div>
    <label for="inputId" class="block text-sm font-semibold text-sky-700 mb-2">
        Label Text
        <span class="text-red-500">*</span>
    </label>
    <input 
        type="text" 
        id="inputId" 
        name="inputName"
        placeholder="Placeholder text"
        required
        class="w-full px-4 py-3 border-2 border-sky-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-500">
    <p class="text-xs text-sky-500 mt-1">Helper text</p>
</div>
```

---

### 6. Button Styles

**Primary Button:**
```html
<button class="px-6 py-3 bg-sky-600 text-white rounded-lg font-semibold hover:bg-sky-700 transition shadow-lg">
    Primary Action
</button>
```

**Secondary Button:**
```html
<button class="px-6 py-3 border-2 border-sky-300 text-sky-700 rounded-lg font-semibold hover:bg-sky-50 transition">
    Secondary Action
</button>
```

**Gradient Button:**
```html
<button class="px-6 py-3 bg-gradient-to-r from-sky-500 to-blue-600 text-white rounded-lg font-semibold hover:from-sky-600 hover:to-blue-700 transition shadow-lg">
    Gradient Action
</button>
```

**Danger Button:**
```html
<button class="px-6 py-3 bg-red-600 text-white rounded-lg font-semibold hover:bg-red-700 transition">
    Delete / Danger
</button>
```

---

### 7. Badge/Tag
```html
<!-- Success Badge -->
<span class="px-3 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
    Completado
</span>

<!-- Warning Badge -->
<span class="px-3 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800">
    Pendiente
</span>

<!-- Danger Badge -->
<span class="px-3 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">
    Cancelado
</span>

<!-- Info Badge -->
<span class="px-3 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
    En progreso
</span>
```

---

### 8. Statistics Card
```html
<div class="bg-white rounded-lg shadow-lg p-6 border-t-4 border-sky-500">
    <div class="flex items-center justify-between">
        <div>
            <p class="text-sm text-sky-600 mb-1">Label</p>
            <p class="text-2xl font-bold text-sky-800">$1,234.56</p>
        </div>
        <div class="bg-sky-100 p-3 rounded-full">
            <svg class="w-8 h-8 text-sky-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <!-- Icon path -->
            </svg>
        </div>
    </div>
</div>
```

---

### 9. Pagination
```javascript
function renderPaginacion(totalItems, itemsPerPage, currentPage) {
    const totalPages = Math.ceil(totalItems / itemsPerPage);
    const container = document.getElementById('paginationContainer');
    
    if (totalPages <= 1) {
        container.innerHTML = '';
        return;
    }
    
    let html = '<div class="flex items-center gap-2">';
    
    // Previous button
    html += `
        <button 
            onclick="cambiarPagina(${currentPage - 1})"
            ${currentPage === 1 ? 'disabled' : ''}
            class="px-4 py-2 border border-sky-300 rounded-lg hover:bg-sky-50 disabled:opacity-50">
            Anterior
        </button>
    `;
    
    // Page numbers
    for (let i = 1; i <= totalPages; i++) {
        html += `
            <button 
                onclick="cambiarPagina(${i})"
                class="px-4 py-2 rounded-lg ${i === currentPage ? 'bg-sky-600 text-white' : 'border border-sky-300 hover:bg-sky-50'}">
                ${i}
            </button>
        `;
    }
    
    // Next button
    html += `
        <button 
            onclick="cambiarPagina(${currentPage + 1})"
            ${currentPage === totalPages ? 'disabled' : ''}
            class="px-4 py-2 border border-sky-300 rounded-lg hover:bg-sky-50 disabled:opacity-50">
            Siguiente
        </button>
    `;
    
    html += '</div>';
    container.innerHTML = html;
}
```

---

### 10. Image Upload with Preview
```html
<div>
    <label class="block text-sm font-semibold text-sky-700 mb-2">Subir Imagen</label>
    <input 
        type="file" 
        id="imageInput" 
        accept="image/*"
        onchange="previewImage(event)"
        class="hidden">
    <label for="imageInput" class="cursor-pointer">
        <div class="border-2 border-dashed border-sky-300 rounded-lg p-8 text-center hover:border-sky-500 transition">
            <img id="imagePreview" src="" alt="Preview" class="hidden mx-auto mb-4 max-h-48 rounded-lg">
            <svg class="w-12 h-12 mx-auto text-sky-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
            </svg>
            <p class="text-sm text-sky-600">Click para seleccionar imagen</p>
        </div>
    </label>
</div>

<script>
function previewImage(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const preview = document.getElementById('imagePreview');
            preview.src = e.target.result;
            preview.classList.remove('hidden');
        };
        reader.readAsDataURL(file);
    }
}
</script>
```

---

### 11. Search Bar
```html
<div class="relative">
    <input 
        type="text" 
        id="searchInput" 
        placeholder="Buscar..."
        class="w-full pl-12 pr-4 py-3 border-2 border-sky-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-500">
    <svg class="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-sky-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
    </svg>
</div>
```

---

### 12. Progress Bar
```html
<div>
    <div class="flex justify-between text-sm mb-2">
        <span class="text-sky-700">$5,000 de $10,000</span>
        <span class="text-sky-700 font-semibold">50%</span>
    </div>
    <div class="w-full bg-sky-200 rounded-full h-3">
        <div class="bg-gradient-to-r from-sky-500 to-blue-600 h-3 rounded-full transition-all" style="width: 50%"></div>
    </div>
</div>
```

---

### 13. Dropdown Menu (Alpine.js)
```html
<div x-data="{ open: false }" class="relative">
    <button @click="open = !open" class="px-4 py-2 bg-sky-600 text-white rounded-lg">
        Menu
        <svg class="inline w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
        </svg>
    </button>
    
    <div x-show="open" @click.away="open = false" 
         class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-10">
        <a href="#" class="block px-4 py-2 text-sm text-sky-700 hover:bg-sky-50">Option 1</a>
        <a href="#" class="block px-4 py-2 text-sm text-sky-700 hover:bg-sky-50">Option 2</a>
        <a href="#" class="block px-4 py-2 text-sm text-sky-700 hover:bg-sky-50">Option 3</a>
    </div>
</div>
```

---

### 14. Tabs
```html
<div class="border-b border-sky-200 mb-6">
    <div class="flex space-x-4">
        <button onclick="showTab('tab1')" id="btnTab1" class="tab-button px-4 py-2 border-b-2 border-sky-600 text-sky-700 font-semibold">
            Tab 1
        </button>
        <button onclick="showTab('tab2')" id="btnTab2" class="tab-button px-4 py-2 text-sky-600 hover:text-sky-700">
            Tab 2
        </button>
        <button onclick="showTab('tab3')" id="btnTab3" class="tab-button px-4 py-2 text-sky-600 hover:text-sky-700">
            Tab 3
        </button>
    </div>
</div>

<div id="contentTab1" class="tab-content">Content 1</div>
<div id="contentTab2" class="tab-content hidden">Content 2</div>
<div id="contentTab3" class="tab-content hidden">Content 3</div>

<script>
function showTab(tabName) {
    // Hide all content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.add('hidden');
    });
    
    // Remove active from all buttons
    document.querySelectorAll('.tab-button').forEach(button => {
        button.classList.remove('border-b-2', 'border-sky-600', 'text-sky-700', 'font-semibold');
        button.classList.add('text-sky-600');
    });
    
    // Show selected content
    document.getElementById(`content${tabName.charAt(0).toUpperCase() + tabName.slice(1)}`).classList.remove('hidden');
    
    // Activate selected button
    document.getElementById(`btn${tabName.charAt(0).toUpperCase() + tabName.slice(1)}`).classList.add('border-b-2', 'border-sky-600', 'text-sky-700', 'font-semibold');
}
</script>
```

---

### 15. Empty State
```html
<div class="p-12 text-center">
    <svg class="mx-auto h-24 w-24 text-sky-200 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"></path>
    </svg>
    <p class="text-sky-600 text-lg mb-4">No se encontraron resultados</p>
    <a href="#" class="inline-block px-6 py-3 bg-sky-600 text-white rounded-lg hover:bg-sky-700">
        Acción Sugerida
    </a>
</div>
```

---

## 🛠 Utility Functions

### Date Formatting
```javascript
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Usage: formatDate('2026-01-15') → "15 de enero de 2026"
```

### Currency Formatting
```javascript
function formatCurrency(amount) {
    return new Intl.NumberFormat('es-MX', {
        style: 'currency',
        currency: 'MXN'
    }).format(amount);
}

// Usage: formatCurrency(1234.56) → "$1,234.56"
```

### Truncate Text
```javascript
function truncate(text, maxLength) {
    if (!text || text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

// Usage: truncate('Long text here', 20) → "Long text here..."
```

---

## 📱 Responsive Classes

```html
<!-- Hidden on mobile, visible on desktop -->
<div class="hidden md:block">Desktop only</div>

<!-- Visible on mobile, hidden on desktop -->
<div class="block md:hidden">Mobile only</div>

<!-- Grid responsive -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    <!-- Auto-adjusts columns based on screen size -->
</div>

<!-- Padding responsive -->
<div class="px-4 md:px-8 lg:px-12">Content</div>

<!-- Text size responsive -->
<h1 class="text-2xl md:text-3xl lg:text-4xl">Heading</h1>
```

---

**Quick Reference Complete!** 🎉
