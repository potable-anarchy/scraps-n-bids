# Scraps n' Bids — Troubleshooting Guide

## Architecture Overview

Scraps n' Bids is a single-page static application:
- **index.html** — Contains all HTML, CSS, and JavaScript
- **images/** — Directory containing meal photos (PNG format)
- **status.html** — Health monitoring dashboard

## Image Handling

### How Images Work

Meal images are stored in the `images/` directory and referenced in the `MEALS` array in `index.html`:

```javascript
ScrapsNBids.MEALS = [
    {
        id: 'tuesdays-pad-thai',
        name: "Tuesday's Pad Thai",
        photo: "images/pad-thai.png",  // <-- image path
        // ...
    },
    // ...
];
```

The `photo` property must point to a valid path relative to the root.

### Available Images

| Filename | Meal |
|----------|------|
| `images/pad-thai.png` | Tuesday's Pad Thai |
| `images/burrito.png` | Half a Burrito |
| `images/stir-fry.png` | Mystery Stir Fry |
| `images/salad.png` | Sad Desk Salad |
| `images/pizza.png` | Quarter Pepperoni Pizza |
| `images/lasagna.png` | Leftover Lasagna Block |

## Common Issues

### Issue: Images Not Loading (404 Errors)

**Symptoms:**
- Status page shows "CRITICAL" or "DEGRADED" status
- Image error rate above 0%
- Broken image icons on main auction page
- Console shows 404 errors for image requests

**Root Cause:**
The `photo` property in the `MEALS` array has an incorrect path. This usually happens when:
- The path prefix is wrong (e.g., `imgs/` instead of `images/`)
- Typo in the filename
- Missing file extension

**Diagnosis:**
1. Check `/status.html` for failed image URLs
2. Compare the failed paths against the actual `images/` directory
3. Look at the `photo` properties in `index.html`

**Fix:**
1. Open `index.html`
2. Find the `MEALS` array (search for `ScrapsNBids.MEALS`)
3. Correct the `photo` property for each meal to use `images/` prefix
4. Ensure filenames match exactly (case-sensitive)

**Example Fix:**
```javascript
// Wrong:
photo: "imgs/pad-thai.png",      // 'imgs' directory doesn't exist
photo: "images/padthai.png",     // missing hyphen
photo: "images/pad-thai",        // missing .png extension

// Correct:
photo: "images/pad-thai.png",
```

### Issue: Auction Not Starting

**Symptoms:**
- Page loads but countdown shows 0:00
- No bids appearing

**Fix:**
Check browser console for JavaScript errors. Common causes:
- Syntax error in MEALS array
- Missing closing brackets

### Issue: Status Page Shows Stale Data

**Symptoms:**
- Status page doesn't reflect recent fixes

**Fix:**
- Hard refresh the page (Ctrl+Shift+R / Cmd+Shift+R)
- Status page auto-refreshes every 30 seconds

## Health Monitoring

The `/status.html` page provides real-time health checks:

- **Overall Status**: HEALTHY / DEGRADED / CRITICAL
- **Image Error Rate**: Percentage of images failing to load
- **Failed URLs**: List of specific images returning 404

Use this page to quickly diagnose asset loading issues.

## File Locations

| Component | Location |
|-----------|----------|
| Application code | `index.html` |
| Meal data (including image paths) | `index.html` → `ScrapsNBids.MEALS` array |
| Image assets | `images/*.png` |
| Status dashboard | `status.html` |
| This guide | `TROUBLESHOOTING.md` |
