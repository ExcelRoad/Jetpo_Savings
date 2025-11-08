# Jetpo Design System Documentation

This document describes the complete design system used in the Jetpo application. Use this guide to maintain consistent design patterns when building new features or creating similar applications.

---

## Table of Contents
1. [Design Philosophy](#design-philosophy)
2. [Color System](#color-system)
3. [Typography](#typography)
4. [Layout & Spacing](#layout--spacing)
5. [Component Library](#component-library)
6. [Navigation](#navigation)
7. [Forms & Inputs](#forms--inputs)
8. [Tables](#tables)
9. [Cards](#cards)
10. [Buttons](#buttons)
11. [Modals & Overlays](#modals--overlays)
12. [Dark Mode](#dark-mode)
13. [RTL Support](#rtl-support)
14. [Icons](#icons)
15. [Animation & Transitions](#animation--transitions)

---

## Design Philosophy

### Core Principles
- **Minimalist & Clean**: Focus on content with minimal distractions
- **Hebrew-First**: Designed for RTL languages with Hebrew as primary language
- **Dark Mode Native**: Both light and dark modes are first-class citizens
- **Accessibility**: Clear contrast, readable fonts, semantic HTML
- **Responsive**: Mobile-first approach with desktop enhancements

### Visual Style
- **Modern Minimalism**: Clean lines, generous whitespace, subtle shadows
- **Neutral Color Palette**: Gray-based with accent colors for actions
- **Soft Corners**: Rounded borders (0.5rem default) for approachability
- **Subtle Interactions**: Smooth transitions, hover states, focus indicators

---

## Color System

### Primary Colors
```css
/* Primary Blue (Used sparingly for primary actions) */
primary-50: #f0f9ff
primary-100: #e0f2fe
primary-200: #bae6fd
primary-300: #7dd3fc
primary-400: #38bdf8
primary-500: #0ea5e9  /* Main primary */
primary-600: #0284c7
primary-700: #0369a1
primary-800: #075985
primary-900: #0c4a6e
```

### Neutral Grays (Main Color System)
```css
/* Light Mode */
gray-50: #f9fafb    /* Hover backgrounds */
gray-100: #f3f4f6   /* Card backgrounds, borders */
gray-200: #e5e7eb   /* Borders, dividers */
gray-300: #d1d5db   /* Input borders */
gray-400: #9ca3af   /* Disabled text */
gray-500: #6b7280   /* Secondary text */
gray-600: #4b5563   /* Body text */
gray-700: #374151   /* Headings */
gray-800: #1f2937   /* Dark text */
gray-900: #111827   /* Black text */

/* Dark Mode */
gray-700: #374151   /* Dark mode cards */
gray-800: #1f2937   /* Dark mode backgrounds */
gray-900: #111827   /* Dark mode page background */
```

### Semantic Colors
```css
/* Success (Green) */
green-600: #16a34a
green-700: #15803d

/* Danger/Error (Red) */
red-500: #ef4444
red-600: #dc2626
red-700: #b91c1c

/* Warning (Yellow) */
yellow-500: #eab308
yellow-600: #ca8a04

/* Info (Blue) */
blue-500: #3b82f6
blue-600: #2563eb

/* Purple (Categories, special states) */
purple-500: #a855f7
purple-600: #9333ea
```

### Usage Guidelines
- **Background**: White (light) / #111827 (dark)
- **Cards**: #f3f4f6 (light) / #1f2937 (dark)
- **Text Primary**: #111827 (light) / #f3f4f6 (dark)
- **Text Secondary**: #6b7280 (light) / #9ca3af (dark)
- **Borders**: #e5e7eb (light) / #374151 (dark)
- **Hover**: #f9fafb (light) / #374151 (dark)

---

## Typography

### Font Family
```css
font-family: 'Rubik', 'Heebo', system-ui, sans-serif;
```

**Rubik** is the primary Hebrew font - clean, modern, and highly readable for Hebrew text.

### Font Sizes
```css
/* Scale */
text-xs: 0.75rem (12px)     /* Small labels, metadata */
text-sm: 0.875rem (14px)    /* Body text, navigation */
text-base: 1rem (16px)      /* Default body text */
text-lg: 1.125rem (18px)    /* Emphasized text */
text-xl: 1.25rem (20px)     /* Subheadings */
text-2xl: 1.5rem (24px)     /* Section titles */
text-3xl: 1.875rem (30px)   /* Page titles */
```

### Font Weights
```css
font-light: 300      /* Rarely used */
font-normal: 400     /* Body text */
font-medium: 500     /* Emphasized text, labels */
font-semibold: 600   /* Headings, buttons */
font-bold: 700       /* Major headings */
```

### Text Styles
```html
<!-- Page Title -->
<h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">

<!-- Section Title -->
<h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">

<!-- Body Text -->
<p class="text-sm text-gray-600 dark:text-gray-400">

<!-- Metadata/Secondary Text -->
<span class="text-xs text-gray-500 dark:text-gray-400">

<!-- Link -->
<a class="text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300">
```

---

## Layout & Spacing

### Container
```html
<div class="max-w-6xl mx-auto px-6 py-12">
  <!-- Content -->
</div>
```
- **Max Width**: 1152px (max-w-6xl)
- **Horizontal Padding**: 1.5rem (24px)
- **Vertical Padding**: 3rem (48px)

### Spacing Scale
```css
/* Tailwind spacing scale used consistently */
1: 0.25rem (4px)
2: 0.5rem (8px)
3: 0.75rem (12px)
4: 1rem (16px)
6: 1.5rem (24px)
8: 2rem (32px)
12: 3rem (48px)
16: 4rem (64px)
```

### Common Patterns
```html
<!-- Section Spacing -->
<div class="mb-8">  <!-- Between major sections -->

<!-- Element Spacing -->
<div class="mb-4">  <!-- Between elements in a section -->

<!-- Gap in Flex/Grid -->
<div class="flex gap-4">  <!-- Between flex items -->
<div class="grid gap-4">  <!-- Between grid items -->
```

---

## Component Library

### 1. Card Component
The most used component in the app - a container with background, border, and padding.

```html
<div class="card">
  <!-- Content -->
</div>
```

**CSS Definition:**
```css
.card {
  background-color: white;
  border: 1px solid #f3f4f6;
  border-radius: 0.5rem;
  padding: 1.5rem;
}

.dark .card {
  background-color: #1f2937;
  border-color: #374151;
}
```

**Variations:**
```html
<!-- Card with hover effect -->
<div class="card hover:shadow-md transition-all">

<!-- Card with overflow (for tables) -->
<div class="card overflow-x-auto">

<!-- Card as clickable link -->
<a href="#" class="card group hover:shadow-md transition-all">
```

---

### 2. Button Styles

#### Primary Button
```html
<button class="btn btn-primary">
  <svg class="w-5 h-5 ml-2">...</svg>
  כפתור ראשי
</button>
```

**CSS:**
```css
.btn {
  display: inline-flex;
  align-items: center;
  padding: 0.75rem 1.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  border-radius: 0.5rem;
  transition: all 0.2s;
}

.btn-primary {
  background-color: #111827;
  color: white;
}
.btn-primary:hover {
  background-color: #374151;
}
.dark .btn-primary {
  background-color: #f3f4f6;
  color: #111827;
}
.dark .btn-primary:hover {
  background-color: #e5e7eb;
}
```

#### Secondary Button
```html
<button class="btn btn-secondary">כפתור משני</button>
```

**CSS:**
```css
.btn-secondary {
  background-color: #f3f4f6;
  color: #374151;
  border: 1px solid #e5e7eb;
}
.btn-secondary:hover {
  background-color: #e5e7eb;
}
.dark .btn-secondary {
  background-color: #374151;
  color: #d1d5db;
  border-color: #4b5563;
}
.dark .btn-secondary:hover {
  background-color: #4b5563;
}
```

#### Icon-Only Button
```html
<button class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
  <svg class="w-5 h-5">...</svg>
</button>
```

---

### 3. Input Styles

```html
<input type="text" class="input" placeholder="טקסט לדוגמה">
<select class="input">...</select>
<textarea class="input" rows="4"></textarea>
```

**CSS:**
```css
.input {
  width: 100%;
  padding: 0.75rem 1rem;
  font-size: 0.875rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  background-color: white;
  color: #111827;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.input:focus {
  outline: none;
  border-color: #0ea5e9;
  box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.1);
}

.dark .input {
  background-color: #1f2937;
  border-color: #4b5563;
  color: #f3f4f6;
}

.dark .input:focus {
  border-color: #0ea5e9;
}
```

---

### 4. Table Styles

```html
<div class="card overflow-x-auto">
  <table class="w-full text-sm">
    <thead>
      <tr class="border-b border-gray-200 dark:border-gray-700">
        <th class="text-right py-3 px-4 font-semibold text-gray-900 dark:text-gray-100">
          כותרת
        </th>
      </tr>
    </thead>
    <tbody>
      <tr class="border-b border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700">
        <td class="py-3 px-4 text-gray-900 dark:text-gray-100">
          תוכן
        </td>
      </tr>
    </tbody>
  </table>
</div>
```

**Key Points:**
- Always wrap in card with `overflow-x-auto`
- Use `text-sm` for table content
- `text-right` for RTL alignment
- Border between rows (not full borders)
- Hover effect on rows
- Padding: py-3 px-4

---

### 5. Grid Layouts

#### Responsive Grid Patterns
```html
<!-- 2-column on mobile, 4-column on desktop -->
<div class="grid grid-cols-2 md:grid-cols-4 gap-4">

<!-- 1-column on mobile, 2-column on tablet, 3-column on desktop -->
<div class="grid md:grid-cols-2 lg:grid-cols-3 gap-4">

<!-- Form grid: 3 columns for filters -->
<div class="grid md:grid-cols-3 gap-4">
```

---

## Navigation

### Navbar Structure
```html
<nav class="border-b border-gray-100 dark:border-gray-800 bg-white dark:bg-gray-900">
  <div class="max-w-6xl mx-auto px-6">
    <div class="flex justify-between items-center h-14">
      <!-- Logo -->
      <a href="/" class="text-lg font-semibold">
        <img src="logo-dark.png" class="h-8 dark:hidden">
        <img src="logo-light.png" class="h-8 hidden dark:block">
        Jetpo
      </a>

      <!-- Navigation Links -->
      <div class="flex items-center gap-6">
        <a href="#" class="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 transition-colors">
          קישור
        </a>
      </div>
    </div>
  </div>
</nav>
```

**Key Points:**
- Height: h-14 (56px)
- Border bottom only
- Links use text-sm
- Hover color transitions
- Logo switches based on dark mode

---

## Forms & Inputs

### Filter Form Pattern
```html
<div class="bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 rounded-lg p-6 mb-6">
  <form method="GET" class="space-y-4">
    <!-- Top Row: Inputs -->
    <div class="grid md:grid-cols-3 gap-4">
      <div>
        <input type="text" name="search" class="input" placeholder="חיפוש...">
      </div>
      <div>
        <select name="filter" class="input">
          <option value="">הכל</option>
        </select>
      </div>
    </div>

    <!-- Bottom Row: Buttons -->
    <div class="flex items-center justify-end gap-2">
      <button type="submit" class="btn btn-primary">סנן</button>
      <a href="?" class="btn btn-secondary">נקה</a>
    </div>
  </form>
</div>
```

### Label Pattern
```html
<div class="mb-4">
  <label for="field" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
    שדה
  </label>
  <input type="text" id="field" name="field" class="input">
</div>
```

---

## Tables

### Comparison Table Pattern
```html
<div class="card overflow-x-auto">
  <table class="w-full text-sm">
    <thead>
      <tr class="border-b border-gray-200 dark:border-gray-700">
        <th class="text-right py-3 px-4 font-semibold text-gray-900 dark:text-gray-100">
          עמודה 1
        </th>
        <th class="text-right py-3 px-4 font-semibold text-gray-900 dark:text-gray-100">
          עמודה 2
        </th>
        <th class="text-center py-3 px-4 font-semibold text-gray-900 dark:text-gray-100">
          פעולות
        </th>
      </tr>
    </thead>
    <tbody>
      <tr class="border-b border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700">
        <td class="py-3 px-4 text-gray-900 dark:text-gray-100">
          ערך 1
        </td>
        <td class="py-3 px-4 text-gray-600 dark:text-gray-400">
          ערך 2
        </td>
        <td class="py-3 px-4 text-center">
          <a href="#" class="text-blue-600 dark:text-blue-400 hover:text-blue-700">
            <svg class="w-5 h-5">...</svg>
          </a>
        </td>
      </tr>
    </tbody>
  </table>
</div>
```

### Color-Coded Values (Returns)
```html
<td class="py-3 px-4 {% if value >= 0 %}text-green-600{% else %}text-red-600{% endif %}">
  {{ value }}%
</td>
```

---

## Cards

### Fund/Item Card Pattern
```html
<div class="card group hover:shadow-md transition-all">
  <a href="/detail/{{ id }}">
    <h3 class="font-semibold text-gray-900 dark:text-gray-100 text-sm mb-1 line-clamp-2 group-hover:text-gray-700 dark:group-hover:text-gray-300">
      כותרת
    </h3>
    <p class="text-xs text-gray-600 dark:text-gray-400 mb-2">
      תיאור משני
    </p>
  </a>

  <div class="flex items-center justify-between pt-3 border-t border-gray-100 dark:border-gray-700">
    <div>
      <div class="text-xs text-gray-500 dark:text-gray-400">תווית</div>
      <div class="text-lg font-semibold text-green-600">+5.2%</div>
    </div>
    <button class="btn btn-primary">פעולה</button>
  </div>
</div>
```

### Quick Action Card
```html
<a href="#" class="card group hover:shadow-md transition-all">
  <div class="flex items-center gap-4">
    <div class="w-12 h-12 bg-gray-100 dark:bg-gray-700 rounded-lg flex items-center justify-center">
      <svg class="w-6 h-6">...</svg>
    </div>
    <div>
      <h3 class="font-semibold text-gray-900 dark:text-gray-100 mb-1">כותרת</h3>
      <p class="text-sm text-gray-600 dark:text-gray-400">תיאור</p>
    </div>
  </div>
</a>
```

---

## Buttons

### All Button Variants

```html
<!-- Primary Action -->
<button class="btn btn-primary">
  <svg class="w-5 h-5 ml-2">...</svg>
  פעולה ראשית
</button>

<!-- Secondary Action -->
<button class="btn btn-secondary">פעולה משנית</button>

<!-- Icon Button -->
<button class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
  <svg class="w-5 h-5">...</svg>
</button>

<!-- Danger Button -->
<button class="px-6 py-3 bg-red-600 text-white text-sm font-semibold rounded-lg hover:bg-red-700 transition-all">
  מחיקה
</button>

<!-- Link as Button -->
<a href="#" class="btn btn-primary">קישור</a>
```

---

## Modals & Overlays

### Modal Structure
```html
<div id="modal" class="hidden fixed inset-0 z-50">
  <!-- Backdrop -->
  <div class="absolute inset-0 bg-black/50 backdrop-blur-sm"></div>

  <!-- Modal Container -->
  <div class="relative h-full flex items-center justify-center p-4">
    <div class="bg-white dark:bg-gray-800 rounded-lg max-w-md w-full p-6 shadow-2xl">
      <!-- Icon -->
      <div class="flex items-start gap-4 mb-6">
        <div class="flex-shrink-0 w-12 h-12 bg-red-100 dark:bg-red-900/30 rounded-full flex items-center justify-center">
          <svg class="w-6 h-6 text-red-600 dark:text-red-400">...</svg>
        </div>
        <div class="flex-grow">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
            כותרת
          </h3>
          <p class="text-sm text-gray-600 dark:text-gray-400">
            תיאור
          </p>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex gap-3">
        <button class="flex-1 px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700">
          אישור
        </button>
        <button class="flex-1 px-6 py-3 bg-white dark:bg-gray-700 border-2 border-gray-200 dark:border-gray-600 rounded-lg">
          ביטול
        </button>
      </div>
    </div>
  </div>
</div>
```

**JavaScript:**
```javascript
function showModal() {
  document.getElementById('modal').classList.remove('hidden');
  document.body.style.overflow = 'hidden';
}

function hideModal() {
  document.getElementById('modal').classList.add('hidden');
  document.body.style.overflow = '';
}
```

---

## Dark Mode

### Implementation
Dark mode is class-based using the `.dark` class on the `<html>` element.

**Initialization Script (in base.html):**
```html
<script>
  if (localStorage.getItem('darkMode') === 'true' ||
      (!localStorage.getItem('darkMode') && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    document.documentElement.classList.add('dark');
  }
</script>
```

**Toggle Function:**
```javascript
function toggleDarkMode() {
  const isDark = document.documentElement.classList.toggle('dark');
  localStorage.setItem('darkMode', isDark);
}
```

### Dark Mode Classes Pattern
```html
<!-- Background -->
<div class="bg-white dark:bg-gray-900">

<!-- Card -->
<div class="bg-white dark:bg-gray-800">

<!-- Text -->
<h1 class="text-gray-900 dark:text-gray-100">
<p class="text-gray-600 dark:text-gray-400">

<!-- Border -->
<div class="border border-gray-200 dark:border-gray-700">

<!-- Hover -->
<button class="hover:bg-gray-50 dark:hover:bg-gray-800">
```

---

## RTL Support

### Base Configuration
```html
<html lang="he" dir="rtl">
```

### CSS Configuration
All layouts naturally support RTL due to:
- Using logical properties where possible
- Tailwind's built-in RTL support
- Flexbox and Grid with reverse directions

### Specific RTL Patterns
```html
<!-- Icon spacing (mr becomes ml in RTL) -->
<svg class="w-5 h-5 ml-2">...</svg>

<!-- Navigation with RTL direction -->
<nav class="flex space-x-reverse space-x-8" dir="rtl">

<!-- Text alignment -->
<th class="text-right">  <!-- Right-aligned for RTL -->
```

---

## Icons

### Icon Library
Using **Heroicons** (outline and solid variants) via inline SVG.

### Icon Sizes
```html
<!-- Small (4x4 - 16px) -->
<svg class="w-4 h-4">

<!-- Medium (5x5 - 20px) - Default -->
<svg class="w-5 h-5">

<!-- Large (6x6 - 24px) -->
<svg class="w-6 h-6">

<!-- Extra Large (8x8 - 32px) -->
<svg class="w-8 h-8">
```

### Icon Colors
```html
<!-- Inherit text color -->
<svg class="w-5 h-5">

<!-- Custom color -->
<svg class="w-5 h-5 text-blue-600 dark:text-blue-400">

<!-- Filled icon -->
<svg class="w-5 h-5 text-red-500 fill-current">
```

---

## Animation & Transitions

### Standard Transitions
```html
<!-- All properties -->
<div class="transition-all">

<!-- Specific properties -->
<div class="transition-colors">
<div class="transition-transform">

<!-- Duration (default is 0.2s) -->
<div class="transition-colors duration-200">
```

### Hover Effects
```html
<!-- Shadow on hover -->
<div class="hover:shadow-md transition-all">

<!-- Scale on hover -->
<button class="hover:scale-105 transition-transform">

<!-- Background on hover -->
<div class="hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
```

### Global Transition
In base.html, all elements have smooth transitions:
```css
* {
  transition: background-color 0.3s ease, border-color 0.3s ease, color 0.3s ease;
}
```

---

## Pagination

### Standard Pagination Pattern
```html
<div class="flex justify-center gap-2">
  {% if page_obj.has_previous %}
  <a href="?page=1" class="btn btn-secondary">ראשון</a>
  <a href="?page={{ page_obj.previous_page_number }}" class="btn btn-secondary">קודם</a>
  {% endif %}

  <span class="btn btn-secondary">
    עמוד {{ page_obj.number }} מתוך {{ page_obj.paginator.num_pages }}
  </span>

  {% if page_obj.has_next %}
  <a href="?page={{ page_obj.next_page_number }}" class="btn btn-secondary">הבא</a>
  <a href="?page={{ page_obj.paginator.num_pages }}" class="btn btn-secondary">אחרון</a>
  {% endif %}
</div>
```

---

## Status Indicators

### Color-Coded Status
```html
<!-- Positive (Green) -->
<span class="text-green-600">+5.2%</span>

<!-- Negative (Red) -->
<span class="text-red-600">-2.1%</span>

<!-- Warning (Yellow) -->
<span class="text-yellow-600">ממתין</span>

<!-- Info (Blue) -->
<span class="text-blue-600">פעיל</span>

<!-- Purple (Special) -->
<span class="text-purple-600">בסקירה</span>
```

### Status Badges
```html
<span class="inline-flex items-center px-3 py-1 rounded-lg text-xs font-medium bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300">
  סטטוס
</span>
```

---

## Empty States

### Standard Empty State
```html
<div class="card text-center py-12">
  <div class="w-16 h-16 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-4">
    <svg class="w-8 h-8 text-gray-400 dark:text-gray-500">...</svg>
  </div>
  <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
    אין פריטים
  </h3>
  <p class="text-gray-600 dark:text-gray-400 mb-6">
    תיאור
  </p>
  <a href="#" class="btn btn-primary">פעולה</a>
</div>
```

---

## Charts & Data Visualization

### Chart.js Integration
```html
<!-- Chart Container -->
<div class="card mb-8">
  <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
    גרף
  </h2>

  <!-- Chart Canvas -->
  <div class="bg-white dark:bg-gray-800 p-4 rounded-lg">
    <canvas id="chart" style="max-height: 400px;"></canvas>
  </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script>
const ctx = document.getElementById('chart');
const isDark = document.documentElement.classList.contains('dark');

new Chart(ctx, {
  type: 'line',
  data: { /* data */ },
  options: {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        labels: {
          color: isDark ? '#e5e7eb' : '#374151',
          font: { family: 'Rubik' }
        }
      }
    },
    scales: {
      y: {
        ticks: {
          color: isDark ? '#9ca3af' : '#6b7280',
          font: { family: 'Rubik' }
        },
        grid: {
          color: isDark ? '#374151' : '#e5e7eb'
        }
      },
      x: {
        ticks: {
          color: isDark ? '#9ca3af' : '#6b7280',
          font: { family: 'Rubik' }
        },
        grid: {
          color: isDark ? '#374151' : '#e5e7eb'
        }
      }
    }
  }
});
</script>
```

### Tab Navigation (for chart filters)
```html
<div class="border-b border-gray-200 dark:border-gray-700">
  <nav class="-mb-px flex space-x-reverse space-x-8 overflow-x-auto" dir="rtl">
    <button class="whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors border-blue-500 text-blue-600 dark:text-blue-400">
      פעיל
    </button>
    <button class="whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300">
      לא פעיל
    </button>
  </nav>
</div>
```

---

## Responsive Breakpoints

### Tailwind Breakpoints
```css
/* Mobile First Approach */
default: 0px      /* Mobile */
sm: 640px         /* Small tablets */
md: 768px         /* Tablets */
lg: 1024px        /* Desktop */
xl: 1280px        /* Large desktop */
2xl: 1536px       /* Extra large desktop */
```

### Common Responsive Patterns
```html
<!-- Grid columns -->
<div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">

<!-- Hidden on mobile -->
<div class="hidden md:block">

<!-- Full width on mobile, constrained on desktop -->
<div class="w-full md:w-auto">

<!-- Flex direction -->
<div class="flex flex-col md:flex-row gap-4">
```

---

## Accessibility

### Focus States
All interactive elements have visible focus states:
```css
.input:focus {
  outline: none;
  border-color: #0ea5e9;
  box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.1);
}
```

### Semantic HTML
- Use proper heading hierarchy (h1, h2, h3)
- Use `<nav>` for navigation
- Use `<button>` for actions, `<a>` for links
- Use `<label>` with inputs
- Use `alt` text for images

### Color Contrast
All text meets WCAG AA standards:
- Body text: #374151 on white (9.56:1)
- Dark mode text: #f3f4f6 on #111827 (14.5:1)

---

## File Structure

### Base Template (base.html)
```html
{% load static %}
<!DOCTYPE html>
<html lang="he" dir="rtl" class="h-full">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{% block title %}Jetpo{% endblock %}</title>
  <link rel="icon" type="image/x-icon" href="{% static 'app_logo/logo-dark.png' %}">
  <link href="{% static 'css/output.css' %}" rel="stylesheet">
  <link href="https://fonts.googleapis.com/css2?family=Rubik:wght@300;400;500;600;700&display=swap" rel="stylesheet">

  <script>
    if (localStorage.getItem('darkMode') === 'true' ||
        (!localStorage.getItem('darkMode') && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
      document.documentElement.classList.add('dark');
    }
  </script>

  {% block extra_css %}{% endblock %}
</head>
<body class="flex flex-col min-h-screen antialiased bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100">
  <!-- Navigation -->
  {% if user.is_authenticated %}
  <nav class="border-b border-gray-100 dark:border-gray-800 bg-white dark:bg-gray-900">
    <!-- Navigation content -->
  </nav>
  {% endif %}

  <!-- Main Content -->
  <main class="flex-grow">
    {% block content %}{% endblock %}
  </main>

  <!-- Footer (if needed) -->

  {% block extra_js %}{% endblock %}
</body>
</html>
```

---

## Tailwind Configuration

### tailwind.config.js
```javascript
module.exports = {
  darkMode: 'class',
  content: [
    './templates/**/*.html',
    './accounts/templates/**/*.html',
    './core/templates/**/*.html',
    './funds/templates/**/*.html',
    './portfolios/templates/**/*.html',
    './knowledge_center/templates/**/*.html',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
        },
      },
      fontFamily: {
        sans: ['Rubik', 'Heebo', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
```

---

## CSS Classes Reference

### Utility Classes Defined in CSS
```css
/* Card */
.card {
  background-color: white;
  border: 1px solid #f3f4f6;
  border-radius: 0.5rem;
  padding: 1.5rem;
}
.dark .card {
  background-color: #1f2937;
  border-color: #374151;
}

/* Button Base */
.btn {
  display: inline-flex;
  align-items: center;
  padding: 0.75rem 1.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  border-radius: 0.5rem;
  transition: all 0.2s;
}

/* Button Primary */
.btn-primary {
  background-color: #111827;
  color: white;
}
.btn-primary:hover {
  background-color: #374151;
}
.dark .btn-primary {
  background-color: #f3f4f6;
  color: #111827;
}
.dark .btn-primary:hover {
  background-color: #e5e7eb;
}

/* Button Secondary */
.btn-secondary {
  background-color: #f3f4f6;
  color: #374151;
  border: 1px solid #e5e7eb;
}
.btn-secondary:hover {
  background-color: #e5e7eb;
}
.dark .btn-secondary {
  background-color: #374151;
  color: #d1d5db;
  border-color: #4b5563;
}
.dark .btn-secondary:hover {
  background-color: #4b5563;
}

/* Input */
.input {
  width: 100%;
  padding: 0.75rem 1rem;
  font-size: 0.875rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  background-color: white;
  color: #111827;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.input:focus {
  outline: none;
  border-color: #0ea5e9;
  box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.1);
}
.dark .input {
  background-color: #1f2937;
  border-color: #4b5563;
  color: #f3f4f6;
}
.dark .input:focus {
  border-color: #0ea5e9;
}
```

---

## Common Patterns Cheat Sheet

### Page Structure
```html
<div class="max-w-6xl mx-auto px-6 py-12">
  <!-- Header -->
  <div class="mb-8">
    <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">
      כותרת עמוד
    </h1>
    <p class="text-gray-600 dark:text-gray-400">תיאור</p>
  </div>

  <!-- Content -->
  <div class="card">
    <!-- Content here -->
  </div>
</div>
```

### List with Cards
```html
<div class="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
  {% for item in items %}
  <div class="card hover:shadow-md transition-all">
    <!-- Card content -->
  </div>
  {% endfor %}
</div>
```

### Form with Validation
```html
<form method="POST">
  {% csrf_token %}
  <div class="mb-4">
    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
      שדה
    </label>
    <input type="text" name="field" class="input" required>
  </div>
  <button type="submit" class="btn btn-primary">שלח</button>
</form>
```

---

## Design Principles Summary

1. **Consistency**: Use the same spacing, colors, and patterns throughout
2. **Hierarchy**: Clear visual hierarchy with font sizes and weights
3. **Whitespace**: Generous spacing between elements
4. **Dark Mode**: Always consider both light and dark appearances
5. **RTL**: Design works naturally in right-to-left
6. **Responsive**: Mobile-first, progressively enhanced for desktop
7. **Accessibility**: Proper focus states, color contrast, semantic HTML
8. **Performance**: Use CSS classes, minimize inline styles, optimize images
9. **Simplicity**: Keep it clean and minimal
10. **Feedback**: Hover states, transitions, and loading indicators

---

## Quick Start Template

```html
{% extends 'base.html' %}

{% block title %}Page Title - Jetpo{% endblock %}

{% block content %}
<div class="max-w-6xl mx-auto px-6 py-12">
  <!-- Header -->
  <div class="mb-8">
    <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">
      כותרת
    </h1>
    <p class="text-gray-600 dark:text-gray-400">תיאור</p>
  </div>

  <!-- Main Content Card -->
  <div class="card">
    <!-- Your content here -->
  </div>
</div>
{% endblock %}
```

---

**End of Design System Documentation**

*This document should be referenced when creating new features or maintaining consistency across the application.*
