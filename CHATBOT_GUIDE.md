# Gift Genius Chatbot POC - User Guide

## 🎁 Project Overview

This is a **Chatbot POC (Proof of Concept)** for Edible.com that provides an AI-powered gift discovery experience. Visitors to the website can use a side widget to access a conversational chatbot that guides them through a gift selection process.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+ (via Pixi)
- OpenAI API key (in `.env` file)

### Running the Application

**Start the API server:**
```bash
cd "D:\Projects\Gift Genius"
pixi run api
```

The server will start at `http://localhost:8000`

**Access the application:**
Open your browser and navigate to:
```
http://localhost:8000
```

## 📱 User Flow

### 1. **Landing Page**
- A modern, clean design similar to Edible.com
- Featured collections showcase
- Navigation bar with options

### 2. **Chatbot Widget** (Right side, fixed position)
- Shows "💬 Need Help Finding a Gift?" button
- Clicking opens the interactive chatbot modal

### 3. **Chatbot Questions** (Sequential flow)
The chatbot guides users through 8 steps:

1. **What's the occasion?**
   - Options: Birthday, Anniversary, Get Well Soon, Congratulations, Thank You, Just Because, Holiday

2. **Budget in mind?** (Optional)
   - Under $50, $50-$100, $100-$200, $200+
   - Skip option available

3. **Same-day delivery needed?** (Optional)
   - Yes / No
   - Skip option available

4. **Recipient's name**
   - Text input field
   - Required field

5. **Pick up to 3 things [Name] would love!** (Optional)
   - Multi-select buttons: Chocolate, Fruit, Brownies, Cookies, Flowers, Teddy Bear, Cake, Pastries
   - Maximum 3 selections
   - Skip option available

6. **Anything [Name] hates?** (Optional)
   - Same options as step 5
   - Skip option available

7. **Is [Name] allergic to anything?** (Optional)
   - Peanuts, Tree nuts, Dairy, Gluten, Shellfish, Eggs
   - Skip option available

8. **Hobbies, interests, or other details?** (Optional)
   - Text area for additional context
   - Skip option available

### 4. **Recommendations Display**
After completing the chatbot:
- Shows 3 product recommendations in card format:
  - **🏆 Best Match** - Top choice matching all preferences
  - **✓ Safe Bet** - Reliable, broadly appealing option
  - **⭐ Something Unique** - Creative, lifestyle-based suggestion

Each card shows:
- Product image placeholder
- Product name
- Price
- Brief description
- AI explanation of why it was recommended
- **Select** button to proceed to checkout
- **Details** button for more information

### 5. **Checkout Page**
- Product summary with price
- Simple checkout form:
  - Full Name
  - Email
  - Shipping Address
  - Card Number
- Confirmation message after completion

### 6. **Sign-Up Page**
After successful checkout:
- Prompt: "Become a Gifting Genius by signing up with us"
- Benefits: Email reminders for birthdays, anniversaries, etc.
- Sign-up form:
  - Full Name
  - Email
  - Password
  - Checkbox for email reminder opt-in
- Success confirmation

## 🔧 Technical Architecture

### Backend
- **Framework:** FastAPI (Python)
- **API Endpoints:**
  - `GET /health` - Health check
  - `POST /api/recommendations` - Get gift recommendations
  - `GET /` - Serve landing page
  - `/static/*` - Static files (CSS, JS, HTML)

### Frontend
- **HTML5, CSS3, JavaScript (ES6+)**
- **Modal-based UI** for chatbot and recommendations
- **Responsive design** - Works on desktop and mobile
- **Real-time form validation**

### AI Integration
- **OpenAI API:**
  - Embeddings: `text-embedding-3-small` for semantic search
  - Chat: `gpt-4o-mini` for recommendations and safety validation
- **Python Libraries:**
  - `FastAPI` - Web framework
  - `Uvicorn` - ASGI server
  - `Pydantic` - Data validation
  - `OpenAI` - API client
  - `Requests` - HTTP library

### Data Flow
1. User fills chatbot form → JavaScript collects data
2. Frontend sends `POST /api/recommendations` with GiftWizardState
3. Backend:
   - Fetches products from Edible API
   - Pre-filters by explicit preferences (Path A)
   - Semantic filtering for unique suggestions (Path B)
   - AI safety validation (no allergens, no dislikes)
   - Ranks products and selects top 3
   - Generates personalized explanations
4. Frontend displays recommendations
5. User selects product → Proceeds to checkout
6. After checkout → Sign-up flow

## 🎨 Features

✅ **Conversational UI** - Natural, guided gift discovery
✅ **Smart Filtering** - Dual-path recommendation engine
✅ **Safety First** - AI validates against allergies/dislikes
✅ **Multi-step Form** - Easy navigation with Previous/Next buttons
✅ **Responsive Design** - Mobile-friendly interface
✅ **Real-time Data** - Connects to actual Edible API
✅ **SKip Options** - Users can bypass optional questions
✅ **Progress Indication** - Clear step tracking

## 🛠️ Development

### File Structure
```
Gift Genius/
├── api/
│   └── main.py                 # FastAPI application
├── lib/
│   ├── edible_api.py          # Edible API client
│   ├── recommender.py         # Recommendation engine
│   ├── scorer.py              # Scoring algorithms
│   ├── ai_client.py           # OpenAI wrapper
│   ├── types.py               # Pydantic models
│   └── database.py            # Persona management
├── static/
│   ├── index.html             # Main page
│   ├── css/
│   │   └── main.css           # Styling
│   ├── js/
│   │   ├── chatbot.js         # Chatbot logic
│   │   └── app.js             # UI handlers
│   └── favicon.svg            # Favicon
└── pixi.toml                  # Project config
```

### Modifying the Chatbot Steps

Edit the `chatbotSteps` array in [static/js/chatbot.js](static/js/chatbot.js) to:
- Add/remove questions
- Change button options
- Adjust validation rules
- Update question text

### Styling Changes

Modify [static/css/main.css](static/css/main.css) to customize:
- Colors (see `:root` CSS variables)
- Layout (grid/flex)
- Animations
- Responsive breakpoints

### API Documentation

**POST /api/recommendations**

Request body:
```json
{
  "occasion": "birthday",
  "budget": "under_50",
  "delivery_date": "2024-02-17T00:00:00",
  "recipient_name": "John",
  "recipient_loves": ["chocolate", "flowers"],
  "recipient_hates": ["nuts"],
  "recipient_allergies": ["peanuts"],
  "recipient_dietary": ["peanuts"],
  "recipient_description": "Loves sports"
}
```

Response:
```json
{
  "success": true,
  "data": {
    "best_match": {
      "product": {...},
      "score": 0.95,
      "category": "best_match",
      "explanation": "This chocolate arrangement..."
    },
    "safe_bet": {...},
    "unique": {...}
  }
}
```

## 🐛 Troubleshooting

### Server won't start
- Ensure `.env` file has valid `OPENAI_API_KEY`
- Check port 8000 is not in use
- Run: `pixi run api`

### Recommendations not loading
- Check browser console for errors (F12)
- Verify API is running (`http://localhost:8000/health`)
- Check network tab to see API request/response
- May be rate-limited by OpenAI API

### Styling looks broken
- Clear browser cache (Ctrl+Shift+Delete)
- Hard refresh (Ctrl+F5)
- Check CSS file loaded in DevTools

## 📊 Future Enhancements

- [ ] User accounts and saved recipients (personas)
- [ ] Email reminders for upcoming occasions
- [ ] Integration with real Edible.com checkout
- [ ] Product reviews and ratings
- [ ] Gift history tracking
- [ ] Wishlist functionality
- [ ] Social sharing of gift picks
- [ ] Mobile app version
- [ ] Advanced filtering (dietary restrictions, eco-friendly, etc.)
- [ ] Multi-language support

## 📝 Notes

- This is a **POC** - Some functionality is simulated (checkout is fake, no actual account creation)
- The recommender uses **OpenAI API** - Each recommendation costs a small amount (fractions of a cent)
- Products are fetched **real-time** from Edible.com API
- All user data in this POC is **not persisted** (no database)

## 🤝 Support

For issues or feature requests, refer to the project README or contact the development team.

---

**Happy Gift Giving! 🎁**
