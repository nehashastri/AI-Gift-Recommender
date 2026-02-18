# 🚀 Quick Reference Guide

## Start Server
```powershell
cd "D:\Projects\Gift Genius"
pixi run api
```
Then open: http://localhost:8000

## API Endpoints

### Health Check
```bash
GET http://localhost:8000/health
```

### Get Recommendations
```bash
POST http://localhost:8000/api/recommendations
Content-Type: application/json

{
  "occasion": "birthday",
  "budget": "under_50",
  "delivery_date": null,
  "recipient_name": "Sarah",
  "recipient_loves": ["chocolate", "flowers"],
  "recipient_hates": ["nuts"],
  "recipient_allergies": ["peanuts"],
  "recipient_dietary": [],
  "recipient_description": "Loves gardening"
}
```

## Project Structure Quick Access

```
Gift Genius/
├── api/main.py                    # ← Backend API code
├── lib/                           # ← AI & Recommendation logic (existing)
├── static/
│   ├── index.html                 # ← Main page
│   ├── css/main.css               # ← All styling (1000+ lines)
│   └── js/
│       ├── chatbot.js             # ← Chatbot flow logic (400+ lines)
│       └── app.js                 # ← Checkout/signup handlers
├── CHATBOT_GUIDE.md               # ← User guide
├── IMPLEMENTATION_SUMMARY.md      # ← What was built
└── pixi.toml                      # ← Project config
```

## Chatbot Steps (in order)

1. **Occasion** (required)
   - Birthday, Anniversary, Get Well, Congratulations, Thank You, Just Because, Holiday

2. **Budget** (optional - skip available)
   - Under $50, $50-100, $100-200, $200+

3. **Same-day Delivery** (optional - skip available)
   - Yes or No

4. **Recipient Name** (required)
   - Text input

5. **What They Love** (optional - max 3 selections)
   - Chocolate, Fruit, Brownies, Cookies, Flowers, Teddy Bear, Cake, Pastries

6. **What They Hate** (optional)
   - Same options as step 5

7. **Allergies** (optional)
   - Peanuts, Tree nuts, Dairy, Gluten, Shellfish, Eggs

8. **Other Details** (optional)
   - Textarea: hobbies/interests/notes

## Key CSS Variables (in main.css)

```css
:root {
    --primary-color: #d4403b;      /* Edible red */
    --secondary-color: #f5f5f5;    /* Light gray */
    --dark-color: #333;             /* Text dark */
    --text-color: #555;             /* Text medium */
    --border-color: #ddd;           /* Borders */
    --shadow: 0 2px 8px ...;
    --shadow-lg: 0 4px 16px ...;
}
```

## Customize the Chatbot

### Add a Question
Edit `static/js/chatbot.js`, in `chatbotSteps` array:

```javascript
{
    id: 'myQuestion',
    question: "Your question?",
    type: 'options', // or 'input', 'toggle-multi', 'input-textarea'
    options: [
        { label: 'Option 1', value: 'opt1' },
        { label: 'Option 2', value: 'opt2' },
    ],
    skipText: 'Skip'
}
```

### Change Colors
Edit `static/css/main.css` `:root` variables:
```css
--primary-color: #yourcolor;
```

### Modify the Backend Response
Edit `api/main.py` `/api/recommendations` endpoint

## Browser Developer Tools

### Check API Requests
1. Open DevTools (F12)
2. Go to **Network** tab
3. Click "Need Help Finding a Gift?"
4. Complete chatbot
5. See POST request to `/api/recommendations`
6. Click it to see Request/Response

### Check Console Errors
1. Open DevTools (F12)
2. Go to **Console** tab
3. Look for red error messages
4. Common issues:
   - CORS errors = API not running
   - 404 errors = File not found
   - API errors = Missing API key

### Inspect Elements
1. DevTools → **Elements** tab
2. Click element to inspect
3. See HTML structure and applied CSS
4. Test CSS changes in real-time

## Troubleshooting

### "connection refused" error
- API not running
- Solution: `pixi run api`

### "404 Not Found" on `/static/...`
- Static files not served
- Solution: Check terminal for errors
- Verify `static/` directory exists

### "OPENAI_API_KEY" error
- Missing or invalid API key
- Solution: Check `.env` file has valid key

### Slow recommendations
- OpenAI API latency (normal)
- Typical: 3-5 seconds
- Check network in DevTools

### Form not submitting
- Check browser console (F12)
- Verify all required fields filled
- Try hard refresh (Ctrl+F5)

## File Sizes

```
index.html        ~15 KB    (HTML structure)
main.css          ~45 KB    (All styling)
chatbot.js        ~20 KB    (Chatbot logic)
app.js            ~8 KB     (UI handlers)
main.py           ~3 KB     (FastAPI routes)
```

## Performance Tips

- Open DevTools Network tab to see load times
- CSS is not minified (easier to customize)
- JavaScript is not bundled (simpler to debug)
- Consider minifying for production:
  - CSS Minifier: https://cssminifier.com
  - JS Minifier: https://javascript-minifier.com

## Mobile Testing

1. Open DevTools (F12)
2. Click device toolbar icon
3. Select device (iPhone, Pixel, etc.)
4. Test responsive design
5. Check touch interactions

## Keyboard Shortcuts

- **Escape** - Close modals
- **Enter** - Submit text input
- **Tab** - Navigate between fields
- **Ctrl+Shift+I** - Open DevTools

## API Response Times

Typical timings:
- Static pages: <50ms
- Health check: <10ms
- Recommendations: 3-8 seconds (includes OpenAI calls)

## Testing Checklist

- [ ] Landing page loads
- [ ] Chatbot widget visible
- [ ] Chatbot opens on click
- [ ] All questions display properly
- [ ] Previous/Next buttons work
- [ ] Skip buttons work for optional fields
- [ ] Form validation works
- [ ] Recommendations load
- [ ] Checkout page shows product
- [ ] Sign-up page appears
- [ ] Completion message shown
- [ ] Works on mobile

## Common Questions

**Q: Can I change the product options?**
A: Edit the `options` array in `chatbotSteps` in `static/js/chatbot.js`

**Q: How do I add more recommendation cards?**
A: Modify the `ThreePickRecommendations` class in `lib/types.py` and update the display in `displayRecommendations()` function

**Q: Can I use this in production?**
A: This is a POC - for production, you'll need:
- Real payment processing
- User authentication/database
- Error handling
- Rate limiting
- API authentication

**Q: How much does it cost to run?**
A: OpenAI API costs ~$0.01-0.05 per recommendation

**Q: Can I host this anywhere?**
A: Yes! This is a standard FastAPI app with static files. Can run on:
- Heroku, Railway, Render (PaaS)
- AWS, Azure, GCP (VMs)
- Docker containers
- Your own server

---

**Last Updated:** February 2026
**Status:** ✅ Ready to Use

