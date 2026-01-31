# Scraps n' Bids

A single-page auction site for unfinished meals - built for the PDD-Toolhouse-rtrvr-ElevenLabs hackathon.

## Overview

Scraps n' Bids is a demo auction site where visitors can watch as unfinished meals are auctioned off one at a time. The site features:

- **Zero dependencies** - Pure HTML, CSS, and vanilla JavaScript in a single file
- **Synthesized bidding** - Automated bid generation simulates an active marketplace
- **Agent-friendly DOM** - Stable IDs and classes for reliable web scraping
- **Sequential auctions** - Automatically cycles through 6 hardcoded meals
- **No backend** - Fully client-side application with in-memory state

## Purpose

This site serves as a demo environment for rtrvr.ai's web agent, providing predictable DOM elements and interactions for agent automation testing during the hackathon.

## Tech Stack

- **HTML5** - Semantic markup with stable element IDs
- **Vanilla JavaScript** - IIFE modules for encapsulation, no frameworks
- **CSS3** - Embedded styles with animations
- **Hosting** - Vercel static deployment

## Running Locally

Since this is a single HTML file with no dependencies, simply open `index.html` in a web browser:

```bash
# Option 1: Open directly in browser
open index.html

# Option 2: Use Python's built-in HTTP server
python3 -m http.server 8000
# Then visit http://localhost:8000

# Option 3: Use Node's http-server (if installed)
npx http-server .
```

## Deployment

Deploy to Vercel with zero configuration:

```bash
# Install Vercel CLI (if needed)
npm i -g vercel

# Deploy
vercel
```

The site will be live in under 30 seconds.

## Architecture

The application is structured as 9 independent modules within a single HTML file:

### Priority 1 - Foundation
1. **HTML Structure** - Semantic layout with agent-friendly IDs
2. **CSS Styles** - Embedded styles with animations
3. **Meal Data** - Hardcoded array of 6 meals
4. **Utility Helpers** - Formatting and random selection functions

### Priority 2 - State
5. **Auction State** - Centralized state management

### Priority 3 - Engines
6. **Timer Module** - Countdown logic
7. **Bidding Engine** - Synthesized bid generation

### Priority 4 - UI
8. **DOM Render** - All UI updates and element manipulation

### Priority 5 - Orchestration
9. **Auction Lifecycle** - Coordinates modules and controls state transitions

## Key Features

### Stable DOM Elements

All critical data points use stable IDs for web scraping:
- `#meal-name` - Current meal name
- `#meal-description` - Meal description
- `#current-bid` - Highest bid amount
- `#countdown` - Remaining time
- `#auction-status` - Auction status (LIVE/SOLD)
- `#meal-progress` - Meal counter (e.g., "2 of 6")
- `#winner-banner` - Winner announcement
- `.bid-entry` - Individual bid entries
- `.bid-amount` - Bid amount within entry
- `.bid-name` - Bidder name within entry

### Synthesized Bidding

Automated bid generation simulates an active marketplace:
- First bid fires 3-8 seconds after auction start
- Subsequent bids fire every 2-6 seconds
- Bid frequency increases in last 10 seconds (1-3s intervals)
- Bid increments: $0.10-$0.75 (normal) or $1.00-$2.00 (jump bids, ~20% chance)
- 12 fictional bidder usernames rotate randomly

### Auction Flow

1. **Page Load** - Initialize meal database, start first auction
2. **During Auction** - Countdown ticks, synthesized bids fire, UI updates live
3. **Auction Close** - Display winner, wait 3 seconds, advance to next meal
4. **End Screen** - Show completion message after all 6 meals

## Success Criteria

- ✅ Loads and runs with zero dependencies (single file, no npm, no build)
- ✅ Auction cycles through all 6 meals automatically
- ✅ Synthesized bids feel natural and varied
- ✅ rtrvr can reliably read meal name, current bid, countdown, and bid history
- ✅ Deploys to Vercel in under 30 seconds
- ✅ Demo loop completes in under 5 minutes

## Development Notes

This project uses Prompt-Driven Development (PDD):
- All code is generated from prompts in the `prompts/` directory
- Architecture is defined in `architecture.json`
- To regenerate code: `pdd sync <module_name>`

## License

MIT
