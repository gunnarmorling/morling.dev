# Favicon Generation Guide

This document describes how the favicon files in this directory were generated.

## Design Specifications

- **Text:** "gm" (lowercase initials)
- **Font:** DejaVu-Sans-Bold (system font)
- **Background Color:** `#73ba30` (site's green accent/link color)
- **Text Color:** `#ECF0F1` (light gray)
- **Font Size:** Proportional to canvas size for optimal visibility

## Files Generated

- `favicon.svg` - Scalable SVG (modern browsers)
- `favicon.ico` - Multi-resolution ICO (16×16 + 32×32)
- `favicon-16x16.png` - Small PNG for browser tabs
- `favicon-32x32.png` - Standard PNG favicon
- `apple-touch-icon.png` - iOS home screen icon (180×180)

## Generation Steps

### 1. Create PNG Favicons

Using ImageMagick's `convert` command:

#### 16×16 PNG
```bash
convert -size 16x16 xc:"#73ba30" \
  -font DejaVu-Sans-Bold \
  -fill "#ECF0F1" \
  -pointsize 11 \
  -gravity center \
  -annotate +0+0 "gm" \
  favicon-16x16.png
```

#### 32×32 PNG
```bash
convert -size 32x32 xc:"#73ba30" \
  -font DejaVu-Sans-Bold \
  -fill "#ECF0F1" \
  -pointsize 22 \
  -gravity center \
  -annotate +0+0 "gm" \
  favicon-32x32.png
```

#### 180×180 Apple Touch Icon
```bash
convert -size 180x180 xc:"#73ba30" \
  -font DejaVu-Sans-Bold \
  -fill "#ECF0F1" \
  -pointsize 120 \
  -gravity center \
  -annotate +0+0 "gm" \
  apple-touch-icon.png
```

### 2. Create Multi-Resolution ICO

Combine the 16×16 and 32×32 PNGs into a single ICO file:

```bash
convert favicon-16x16.png favicon-32x32.png \
  -colors 256 \
  favicon.ico
```

This creates an ICO file containing both sizes for compatibility with different display contexts.

### 3. Create SVG Favicon

The SVG was created manually for optimal scalability:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <!-- Green background - matching link color -->
  <rect width="100" height="100" fill="#73ba30"/>

  <!-- Text "gm" using system fonts with fallbacks -->
  <text
    x="50"
    y="50"
    font-family="DejaVu Sans, Arial, Helvetica, sans-serif"
    font-size="78"
    font-weight="bold"
    fill="#ECF0F1"
    text-anchor="middle"
    dominant-baseline="central">gm</text>
</svg>
```

**Font size note:** The SVG uses `font-size="78"` to make the letters extend slightly beyond the edges, matching the cropped appearance of the PNG versions.

## ImageMagick Command Breakdown

### Key Parameters

- **`-size WxH`** - Canvas dimensions
- **`xc:"#73ba30"`** - Fill canvas with solid color (xc = X Color)
- **`-font DejaVu-Sans-Bold`** - Font family (system font)
- **`-fill "#ECF0F1"`** - Text color
- **`-pointsize N`** - Font size in points
- **`-gravity center`** - Center text horizontally and vertically
- **`-annotate +0+0 "gm"`** - Draw text at position with offsets
- **`-colors 256`** - Reduce to 256 colors (for ICO compatibility)

## Font Selection

### Why DejaVu-Sans-Bold?

1. **Universal availability** - Pre-installed on most Linux systems
2. **No licensing issues** - Free and open source
3. **Excellent rendering** - Clear and legible at small sizes
4. **Bold weight** - Ensures visibility in tiny favicon sizes

### Checking Available Fonts

To see available fonts in ImageMagick:

```bash
convert -list font
```

To verify DejaVu Sans is available:

```bash
convert -list font | grep -i dejavu
```

## Color Scheme

The green color `#73ba30` was chosen to match the site's accent color used throughout:
- Link hover states
- Table of Contents borders
- Table headers
- Tag hover backgrounds
- Code block callout numbers

This creates visual consistency between the favicon and the site's branding.

## Browser Compatibility

### Which File Gets Used?

- **Modern browsers (Chrome, Firefox, Safari):** `favicon.svg` (scalable, perfect quality)
- **Standard browsers:** `favicon-32x32.png` or `favicon-16x16.png` (good quality)
- **Legacy browsers (IE, old Edge):** `favicon.ico` (universal fallback)
- **iOS/iPadOS home screen:** `apple-touch-icon.png` (180×180)

### HTML Integration

The favicons are referenced in the theme's header (`layouts/partials/header.html`):

```html
<!-- Favicons -->
<link rel="icon" type="image/svg+xml" href="/favicon.svg" />
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png" />
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png" />
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
<link rel="shortcut icon" href="/favicon.ico" />
```

## Regenerating Favicons

### Prerequisites

```bash
# Check ImageMagick is installed
convert --version

# Verify DejaVu-Sans-Bold is available
convert -list font | grep "DejaVu-Sans-Bold"
```

### Quick Regeneration Script

```bash
#!/bin/bash
# Navigate to the favicon directory
cd /path/to/themes/ezhil/static/

# Generate PNGs
convert -size 16x16 xc:"#73ba30" -font DejaVu-Sans-Bold -fill "#ECF0F1" \
  -pointsize 11 -gravity center -annotate +0+0 "gm" favicon-16x16.png

convert -size 32x32 xc:"#73ba30" -font DejaVu-Sans-Bold -fill "#ECF0F1" \
  -pointsize 22 -gravity center -annotate +0+0 "gm" favicon-32x32.png

convert -size 180x180 xc:"#73ba30" -font DejaVu-Sans-Bold -fill "#ECF0F1" \
  -pointsize 120 -gravity center -annotate +0+0 "gm" apple-touch-icon.png

# Generate ICO
convert favicon-16x16.png favicon-32x32.png -colors 256 favicon.ico

echo "✓ Favicons generated successfully!"
```

## Customization Options

### Change Colors

Replace `#73ba30` (background) or `#ECF0F1` (text) with your preferred colors:

```bash
convert -size 32x32 xc:"#YOUR_BG_COLOR" \
  -font DejaVu-Sans-Bold \
  -fill "#YOUR_TEXT_COLOR" \
  -pointsize 22 \
  -gravity center \
  -annotate +0+0 "gm" \
  favicon-32x32.png
```

### Change Text

Replace `"gm"` with your desired text (keep it short - 1-3 characters work best):

```bash
convert -size 32x32 xc:"#73ba30" \
  -font DejaVu-Sans-Bold \
  -fill "#ECF0F1" \
  -pointsize 22 \
  -gravity center \
  -annotate +0+0 "ABC" \
  favicon-32x32.png
```

### Use Different Font

Replace `DejaVu-Sans-Bold` with another available font:

```bash
convert -size 32x32 xc:"#73ba30" \
  -font "Your-Font-Name" \
  -fill "#ECF0F1" \
  -pointsize 22 \
  -gravity center \
  -annotate +0+0 "gm" \
  favicon-32x32.png
```

## Troubleshooting

### Font Not Found Error

If you get `unable to read font` error:

1. Check available fonts: `convert -list font`
2. Use the exact font name from the list
3. Or specify font file path: `-font /path/to/font.ttf`

### Text Too Small/Large

Adjust the `-pointsize` value:
- **16×16:** Try values between 9-13
- **32×32:** Try values between 18-26
- **180×180:** Try values between 100-140

### Text Off-Center

The `-gravity center` should center text automatically. If it appears off:
- Check font metrics (some fonts have unusual baselines)
- Try different fonts
- Adjust position: `-annotate +X+Y "text"` (use negative values to shift)

## Version History

- **2025-12-14:** Initial favicon set created
  - Text: "gm" (lowercase)
  - Font: DejaVu-Sans-Bold
  - Colors: #73ba30 background, #ECF0F1 text
  - Sizes: 16×16, 32×32, 180×180, ICO, SVG

## Tools Used

- **ImageMagick 6.9+** - Image generation and manipulation
- **Text editor** - For creating SVG file
- **Browser DevTools** - For testing favicon display

## References

- [ImageMagick Documentation](https://imagemagick.org/index.php)
- [Favicon Best Practices](https://web.dev/learn/pwa/app-design/#icons-and-graphics)
- [SVG Favicon Support](https://caniuse.com/link-icon-svg)
