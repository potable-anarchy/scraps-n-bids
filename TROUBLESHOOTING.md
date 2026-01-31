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

### Issue: Auction Stuck After "SOLD" (Transition Delay)

**Symptoms:**
- Status page shows "CRITICAL" with "Auction transitions stalled"
- Auction Transition metric shows minutes instead of seconds
- After an auction ends with "SOLD", nothing happens for a very long time
- Users report the app appears frozen after a winner is announced

**Root Cause:**
The `AUCTION_TRANSITION_DELAY` constant in `index.html` is set too high. This controls how long the winner banner displays before the next auction starts. Normal value is `3000` (3 seconds). If accidentally set to `300000` (5 minutes) or higher, auctions appear stuck.

**Diagnosis:**
1. Check `/status.html` — look at "Auction Transition" metric
2. If it shows minutes (e.g., "5.0m") instead of seconds, the delay is too high
3. Search `index.html` for `AUCTION_TRANSITION_DELAY`

**Fix:**
1. Open `index.html`
2. Find `AUCTION_TRANSITION_DELAY` in the MODULE 9: AUCTION LIFECYCLE section
3. Change the value back to `3000` (3 seconds)

**Example Fix:**
```javascript
// Wrong - auctions stuck for 5 minutes:
var AUCTION_TRANSITION_DELAY = 300000;

// Correct - 3 second delay:
var AUCTION_TRANSITION_DELAY = 3000;
```

**Acceptable Range:**
- Normal: 1000-5000ms (1-5 seconds)
- Slow but acceptable: 5000-30000ms (5-30 seconds)  
- Broken: >30000ms (over 30 seconds)

---

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
- **Image Assets**: Error rate for meal photos
- **Images Loaded/Failed**: Counts of successful and failed image loads
- **Auction Transition**: Time between auctions (should be ~3 seconds)
- **Failed URLs**: List of specific images returning 404

Use this page to quickly diagnose issues. The page auto-refreshes every 30 seconds.

## File Locations

| Component | Location |
|-----------|----------|
| Application code | `index.html` |
| Meal data (including image paths) | `index.html` → `ScrapsNBids.MEALS` array |
| Auction transition delay | `index.html` → `AUCTION_TRANSITION_DELAY` constant |
| Image assets | `images/*.png` |
| Status dashboard | `status.html` |
| This guide | `TROUBLESHOOTING.md` |
