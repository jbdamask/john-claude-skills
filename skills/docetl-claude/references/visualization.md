# DocETL Visualization Guidelines

Guidelines for creating reports and visualizations from DocETL pipeline outputs.

## Design Principles

### Visual Aesthetics

- **Clean and minimalist** - no clutter, generous whitespace
- **Warm and elegant color theme** - 1-2 accent colors max
- **Subtle borders** - not too rounded (border-radius: 8-10px max)
- **Sans-serif fonts** - system fonts like -apple-system, Segoe UI, Roboto
- **Light background** - off-white (#f5f5f5) with white cards for content

### Report Structure

1. Title + "Created by DocETL" subtitle
2. Key stats cards (document count, categories, etc.)
3. Distribution charts (bar charts, pie charts)
4. Summary table with detailed analysis
5. Minimal footer

### Chart and Table Mix

- **Charts** for distributions, trends, comparisons
- **Tables** for detailed summaries, lists, drill-down data
- Balance both - don't use only one type

## Interactive Elements

### Expandable Content

**All truncated content must be expandable** - never use static "..." truncation.

- Long text: Show first ~250 chars with "(show more)" toggle
- Long lists: Show first 4-6 items with "(+N more)" toggle
- Use JavaScript to toggle visibility, not page reloads

Example pattern:
```html
<span class="preview">First 250 characters...</span>
<span class="full-content" style="display:none">Full content here...</span>
<a class="toggle-link" onclick="toggleContent(this)">(show more)</a>
```

### Source Document Links

**Link aggregated results to source documents** - users should be able to drill down.

- Clickable links that open a modal/popup with source content
- Modal should show: extracted fields + original source text
- Original text can be collapsed by default with "Show original" toggle
- Embed source data as JSON in the page for JavaScript access

Example pattern:
```html
<script>
const sourceData = {{ source_documents | tojson }};
</script>
<a onclick="showSource('doc-123')">View source</a>
```

## Color Palette

### Recommended Colors

```css
/* Background */
--bg-light: #f5f5f5;
--bg-card: #ffffff;

/* Text */
--text-primary: #333333;
--text-secondary: #666666;

/* Accent (choose one pair) */
--accent-blue: #4a90d9;
--accent-blue-light: #e8f0fa;

--accent-teal: #2d9cdb;
--accent-teal-light: #e3f5fc;

--accent-coral: #e07b67;
--accent-coral-light: #fdf0ed;

/* Status */
--success: #48bb78;
--warning: #ecc94b;
--error: #f56565;
```

## Typography

### Font Stack

```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
```

### Hierarchy

- **Title**: 24-28px, bold
- **Subtitle**: 14-16px, normal weight, muted color
- **Section headers**: 18-20px, semibold
- **Body text**: 14-16px, normal
- **Small text/labels**: 12px, muted color

## Example HTML Structure

```html
<!DOCTYPE html>
<html>
<head>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: #f5f5f5;
      margin: 0;
      padding: 20px;
    }
    .container { max-width: 1200px; margin: 0 auto; }
    .card {
      background: white;
      border-radius: 8px;
      padding: 20px;
      margin-bottom: 20px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .title { font-size: 28px; font-weight: bold; margin-bottom: 4px; }
    .subtitle { font-size: 14px; color: #666; margin-bottom: 24px; }
    .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 16px; }
    .stat-card { background: #f8f9fa; padding: 16px; border-radius: 8px; text-align: center; }
    .stat-value { font-size: 32px; font-weight: bold; color: #4a90d9; }
    .stat-label { font-size: 12px; color: #666; margin-top: 4px; }
  </style>
</head>
<body>
  <div class="container">
    <div class="card">
      <div class="title">Analysis Report</div>
      <div class="subtitle">Created by DocETL</div>

      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-value">{{ doc_count }}</div>
          <div class="stat-label">Documents</div>
        </div>
        <!-- More stats... -->
      </div>
    </div>

    <!-- Charts, tables, etc. -->
  </div>
</body>
</html>
```
