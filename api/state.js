import { kv } from '@vercel/kv';

// Meal data (same as client)
const MEALS = [
  { id: 'tuesdays-pad-thai', name: "Tuesday's Pad Thai", description: "Was going to finish it but then someone mentioned cake in the break room.", category: 'asian', startingBid: 1.50, photo: 'images/pad-thai.png', auctionDuration: 45 },
  { id: 'half-a-burrito', name: 'Half a Burrito', description: "The good half. Someone already took the end with all the sour cream.", category: 'mexican', startingBid: 2.00, photo: 'images/burrito.png', auctionDuration: 40 },
  { id: 'mystery-stir-fry', name: 'Mystery Stir Fry', description: "It was definitely vegetables at some point. Could be anything now.", category: 'asian', startingBid: 1.00, photo: 'images/stir-fry.png', auctionDuration: 35 },
  { id: 'sad-desk-salad', name: 'Sad Desk Salad', description: "Wilting gracefully since 11:30 AM. Dressing on the side (missing).", category: 'american', startingBid: 0.75, photo: 'images/salad.png', auctionDuration: 40 },
  { id: 'quarter-pepperoni-pizza', name: 'Quarter Pepperoni Pizza', description: "Three slices already claimed. This is the survivor. Slightly cold.", category: 'american', startingBid: 3.00, photo: 'images/pizza.png', auctionDuration: 50 },
  { id: 'leftover-lasagna-block', name: 'Leftover Lasagna Block', description: "A dense cube of layered perfection. Microwave at your own risk.", category: 'italian', startingBid: 2.50, photo: 'images/lasagna.png', auctionDuration: 45 },
];

const BIDDERS = [
  'FoodieGregory', 'BargainBeth', 'SnackAttack99', 'ThriftyTina',
  'LunchLarry', 'DealDave', 'MealStealer', 'CheapEats_Carol',
  'BidKing_Tom', 'LeftoverLove', 'BargainHunter_X', 'PricePete'
];

function randomChoice(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

function randomBidIncrement(isJump) {
  if (isJump) {
    return +(1.00 + Math.random() * 1.00).toFixed(2);
  }
  return +(0.10 + Math.random() * 0.65).toFixed(2);
}

async function initializeAuction() {
  const mealIndex = Math.floor(Math.random() * MEALS.length);
  const meal = MEALS[mealIndex];

  const state = {
    mealIndex,
    meal,
    bids: [],
    startedAt: Date.now(),
    status: 'active',
    lastBidAt: Date.now(),
    winner: null
  };

  await kv.set('auction_state', state);
  return state;
}

async function tickAuction(state) {
  const now = Date.now();
  const elapsed = (now - state.startedAt) / 1000;
  const remaining = state.meal.auctionDuration - elapsed;

  // Auction ended
  if (remaining <= 0 && state.status === 'active') {
    state.status = 'sold';
    if (state.bids.length > 0) {
      state.winner = state.bids[state.bids.length - 1];
    }
    state.soldAt = now;
    await kv.set('auction_state', state);
    return state;
  }

  // Transition to next auction after 3 seconds
  if (state.status === 'sold' && (now - state.soldAt) > 3000) {
    return await initializeAuction();
  }

  // Generate synthetic bids
  if (state.status === 'active') {
    const timeSinceLastBid = (now - state.lastBidAt) / 1000;

    // Bid timing logic
    let shouldBid = false;
    if (state.bids.length === 0 && timeSinceLastBid > 3) {
      // First bid after 3 seconds
      shouldBid = true;
    } else if (remaining <= 10 && timeSinceLastBid > 1.5) {
      // Last 10 seconds: faster bidding
      shouldBid = Math.random() < 0.6;
    } else if (timeSinceLastBid > 3) {
      // Normal: bid every 3-6 seconds
      shouldBid = Math.random() < 0.4;
    }

    if (shouldBid) {
      const bidder = randomChoice(BIDDERS);
      const currentHigh = state.bids.length > 0
        ? state.bids[state.bids.length - 1].amount
        : state.meal.startingBid;
      const isJump = Math.random() < 0.2;
      const increment = randomBidIncrement(isJump);
      const amount = +(currentHigh + increment).toFixed(2);

      state.bids.push({
        bidder,
        amount,
        timestamp: now
      });
      state.lastBidAt = now;
      await kv.set('auction_state', state);
    }
  }

  return state;
}

export default async function handler(req, res) {
  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Cache-Control', 'no-store');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  try {
    let state = await kv.get('auction_state');

    // Initialize if no state exists
    if (!state) {
      state = await initializeAuction();
    } else {
      // Tick the auction forward
      state = await tickAuction(state);
    }

    // Calculate remaining time for client
    const now = Date.now();
    const elapsed = (now - state.startedAt) / 1000;
    const remaining = Math.max(0, state.meal.auctionDuration - elapsed);

    res.status(200).json({
      ...state,
      remaining: Math.ceil(remaining),
      serverTime: now
    });
  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
}
