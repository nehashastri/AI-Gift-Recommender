// Chatbot state
const chatbotState = {
    currentStep: 0,
    occasion: '',
    budget: '',
    sameDayDelivery: false,
    recipientName: '',
    loves: [],
    hates: [],
    allergies: [],
    interests: '',
};

// Define chatbot steps
const chatbotSteps = [
    {
        id: 'occasion',
        question: "What's the occasion?",
        type: 'options',
        options: [
            { label: 'Birthday', value: 'birthday' },
            { label: 'Anniversary', value: 'anniversary' },
            { label: 'Get Well Soon', value: 'get_well' },
            { label: 'Congratulations', value: 'congratulations' },
            { label: 'Thank You', value: 'thank_you' },
            { label: 'Just Because', value: 'just_because' },
            { label: 'Holiday', value: 'holiday' },
        ],
    },
    {
        id: 'budget',
        question: 'Do you have a budget in mind?',
        type: 'options-skip',
        options: [
            { label: 'Under $50', value: 'under_50' },
            { label: '$50 - $100', value: '50_100' },
            { label: '$100 - $200', value: '100_200' },
            { label: '$200+', value: '200_plus' },
        ],
        skipText: 'Skip',
    },
    {
        id: 'sameDayDelivery',
        question: 'Do you need same-day delivery?',
        type: 'options-skip',
        options: [
            { label: 'Yes', value: true },
            { label: 'No', value: false },
        ],
        skipText: 'Skip',
    },
    {
        id: 'recipientName',
        question: "What's the recipient's name?",
        type: 'input',
        placeholder: 'Enter their name',
    },
    {
        id: 'loves',
        question: "Pick up to 3 things _name_ would love!",
        type: 'toggle-multi',
        maxSelect: 3,
        options: [
            { label: '🍫 Chocolate', value: 'chocolate' },
            { label: '🍓 Fruit', value: 'fruit' },
            { label: '🧁 Brownies', value: 'brownies' },
            { label: '🍪 Cookies', value: 'cookies' },
            { label: '🌸 Flowers', value: 'flowers' },
            { label: '🧸 Teddy Bear', value: 'teddy_bear' },
            { label: '🎂 Cake', value: 'cake' },
            { label: '🍰 Pastries', value: 'pastries' },
        ],
        skipText: 'Skip',
    },
    {
        id: 'hates',
        question: "Is there anything _name_ hates?",
        type: 'toggle-multi',
        options: [
            { label: '🍫 Chocolate', value: 'chocolate' },
            { label: '🍓 Fruit', value: 'fruit' },
            { label: '🧁 Brownies', value: 'brownies' },
            { label: '🍪 Cookies', value: 'cookies' },
            { label: '🌸 Flowers', value: 'flowers' },
            { label: '🧸 Teddy Bear', value: 'teddy_bear' },
            { label: '🎂 Cake', value: 'cake' },
            { label: '🍰 Pastries', value: 'pastries' },
        ],
        skipText: 'Skip',
    },
    {
        id: 'allergies',
        question: "Is _name_ allergic to anything?",
        type: 'toggle-multi',
        options: [
            { label: '🥜 Peanuts', value: 'peanuts' },
            { label: '🌰 Tree nuts', value: 'tree_nuts' },
            { label: '🥛 Dairy', value: 'dairy' },
            { label: '🌾 Gluten', value: 'gluten' },
            { label: '🍤 Shellfish', value: 'shellfish' },
            { label: '🥚 Eggs', value: 'eggs' },
        ],
        skipText: 'Skip',
    },
    {
        id: 'interests',
        question: 'Anything else you want to share about _name_? (hobbies, interests, etc.)',
        type: 'input-textarea',
        placeholder: 'E.g., loves gardening, enjoys cooking, sports enthusiast...',
        skipText: 'Skip',
    },
];

// Initialize chatbot
function initChatbot() {
    console.log('[CHATBOT] Initializing...');
    const chatbotToggle = document.getElementById('chatbot-toggle');
    const closeBtn = document.getElementById('close-chatbot');
    const nextBtn = document.getElementById('next-btn');
    const prevBtn = document.getElementById('prev-btn');

    chatbotToggle.addEventListener('click', openChatbot);
    closeBtn.addEventListener('click', closeChatbot);
    nextBtn.addEventListener('click', nextStep);
    prevBtn.addEventListener('click', prevStep);

    // Render first step
    console.log('[CHATBOT] Initialization complete. Rendering first step...');
    renderStep();
}

function openChatbot() {
    console.log('[CHATBOT] Opening chatbot modal');
    document.getElementById('chatbot-modal').classList.add('show');
}

function closeChatbot() {
    console.log('[CHATBOT] Closing chatbot modal');
    document.getElementById('chatbot-modal').classList.remove('show');
    // Reset if user closes without completing
}

function renderStep() {
    const step = chatbotSteps[chatbotState.currentStep];
    const body = document.getElementById('chatbot-body');
    const nextBtn = document.getElementById('next-btn');
    const prevBtn = document.getElementById('prev-btn');

    console.log(`[CHATBOT] Rendering step ${chatbotState.currentStep}/${chatbotSteps.length - 1}: ${step.id}`, step);

    body.innerHTML = '';

    // Create step container
    const stepDiv = document.createElement('div');
    stepDiv.className = 'chatbot-step active';

    // Question
    const question = step.question.replace('_name_', chatbotState.recipientName || 'they');
    const questionDiv = document.createElement('div');
    questionDiv.className = 'step-question';
    questionDiv.textContent = question;
    stepDiv.appendChild(questionDiv);

    // Render based on type
    if (step.type === 'options' || step.type === 'options-skip') {
        const options = document.createElement('div');
        options.className = 'step-options';

        step.options.forEach((option) => {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'option-button';
            btn.textContent = option.label;

            if (chatbotState[step.id] === option.value) {
                btn.classList.add('selected');
            }

            btn.addEventListener('click', () => {
                document.querySelectorAll('.option-button').forEach((b) => {
                    b.classList.remove('selected');
                });
                btn.classList.add('selected');
                chatbotState[step.id] = option.value;
            });

            options.appendChild(btn);
        });

        // Add skip button if applicable
        if (step.skipText) {
            const skipBtn = document.createElement('button');
            skipBtn.type = 'button';
            skipBtn.className = 'option-button';
            skipBtn.textContent = `⊘ ${step.skipText}`;
            skipBtn.style.opacity = '0.6';

            skipBtn.addEventListener('click', () => {
                chatbotState[step.id] = null;
                nextStep();
            });

            options.appendChild(skipBtn);
        }

        stepDiv.appendChild(options);
    } else if (step.type === 'input') {
        const input = document.createElement('input');
        input.type = 'text';
        input.className = 'step-input';
        input.placeholder = step.placeholder;
        input.value = chatbotState[step.id] || '';

        input.addEventListener('change', (e) => {
            chatbotState[step.id] = e.target.value;
        });

        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                nextStep();
            }
        });

        stepDiv.appendChild(input);

        // Auto-focus
        setTimeout(() => input.focus(), 100);
    } else if (step.type === 'input-textarea') {
        const textarea = document.createElement('textarea');
        textarea.className = 'step-input';
        textarea.placeholder = step.placeholder;
        textarea.value = chatbotState[step.id] || '';
        textarea.style.minHeight = '100px';
        textarea.style.resize = 'vertical';

        textarea.addEventListener('change', (e) => {
            chatbotState[step.id] = e.target.value;
        });

        stepDiv.appendChild(textarea);

        // Add skip button
        if (step.skipText) {
            const skipBtn = document.createElement('button');
            skipBtn.type = 'button';
            skipBtn.className = 'option-button';
            skipBtn.textContent = `⊘ ${step.skipText}`;
            skipBtn.style.marginTop = '1rem';
            skipBtn.style.opacity = '0.6';
            skipBtn.style.width = '100%';

            skipBtn.addEventListener('click', () => {
                chatbotState[step.id] = '';
                nextStep();
            });

            stepDiv.appendChild(skipBtn);
        }

        setTimeout(() => textarea.focus(), 100);
    } else if (step.type === 'toggle-multi') {
        const toggleGroup = document.createElement('div');
        toggleGroup.className = 'toggle-group';

        // Filter options based on step rules
        let filteredOptions = step.options;

        // If this is the "hates" step, exclude items that were selected as "loves"
        if (step.id === 'hates' && chatbotState.loves && chatbotState.loves.length > 0) {
            filteredOptions = step.options.filter(option =>
                !chatbotState.loves.includes(option.value)
            );
        }

        filteredOptions.forEach((option) => {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'option-button toggle';
            btn.textContent = option.label;

            if (chatbotState[step.id]?.includes(option.value)) {
                btn.classList.add('selected');
            }

            btn.addEventListener('click', () => {
                const index = chatbotState[step.id].indexOf(option.value);
                if (index > -1) {
                    chatbotState[step.id].splice(index, 1);
                    btn.classList.remove('selected');
                } else {
                    if (step.maxSelect && chatbotState[step.id].length >= step.maxSelect) {
                        alert(`You can select up to ${step.maxSelect} items`);
                        return;
                    }
                    chatbotState[step.id].push(option.value);
                    btn.classList.add('selected');
                }
                updateSelectedItems(step, step.id);
            });

            toggleGroup.appendChild(btn);
        });

        stepDiv.appendChild(toggleGroup);

        // Show selected items
        if (chatbotState[step.id]?.length > 0) {
            updateSelectedItems(step, step.id);
        }

        // Add skip button
        if (step.skipText) {
            const skipBtn = document.createElement('button');
            skipBtn.type = 'button';
            skipBtn.className = 'option-button';
            skipBtn.textContent = `⊘ ${step.skipText}`;
            skipBtn.style.marginTop = '1rem';
            skipBtn.style.opacity = '0.6';
            skipBtn.style.width = '100%';

            skipBtn.addEventListener('click', () => {
                chatbotState[step.id] = [];
                nextStep();
            });

            stepDiv.appendChild(skipBtn);
        }
    }

    // Initialize array for toggle-multi if not exists
    if ((step.type === 'toggle-multi') && !Array.isArray(chatbotState[step.id])) {
        chatbotState[step.id] = [];
    }

    body.appendChild(stepDiv);

    // Update button visibility
    prevBtn.style.display = chatbotState.currentStep > 0 ? 'block' : 'none';

    // Change next button text on last step
    if (chatbotState.currentStep === chatbotSteps.length - 1) {
        nextBtn.textContent = 'Get Recommendations →';
    } else {
        nextBtn.textContent = 'Next →';
    }
}

function updateSelectedItems(step, stepId) {
    let container = document.querySelector('.selected-items');
    if (!container) {
        container = document.createElement('div');
        container.className = 'selected-items';
        document.querySelector('.chatbot-step').appendChild(container);
    }

    const selected = chatbotState[stepId] || [];
    const items = selected
        .map((val) => {
            const option = step.options.find((o) => o.value === val);
            return option ? option.label : val;
        })
        .join(', ');

    container.innerHTML = `
        <p>Selected (${selected.length}/${step.maxSelect || 'unlimited'}):</p>
        <div class="selected-items-list">
            ${selected
            .map((val) => {
                const option = step.options.find((o) => o.value === val);
                return `<span class="selected-item">${option ? option.label : val}</span>`;
            })
            .join('')}
        </div>
    `;
}

function nextStep() {
    const step = chatbotSteps[chatbotState.currentStep];

    console.log(`[CHATBOT] Step ${chatbotState.currentStep}: ${step.id}`, chatbotState);

    // Validate current step
    if (step.type === 'input' && !chatbotState[step.id]) {
        alert('Please enter a value');
        return;
    }

    if (chatbotState.currentStep === chatbotSteps.length - 1) {
        // Last step - submit
        console.log('[CHATBOT] Last step reached. Calling submitChatbot()...');
        submitChatbot();
        return;
    }

    chatbotState.currentStep++;
    renderStep();
}

function prevStep() {
    if (chatbotState.currentStep > 0) {
        chatbotState.currentStep--;
        renderStep();
    }
}

async function submitChatbot() {
    console.log('[API] submitChatbot() called');
    console.log('[API] Current chatbotState:', chatbotState);

    const modal = document.getElementById('chatbot-modal');
    const nextBtn = document.getElementById('next-btn');
    const body = document.getElementById('chatbot-body');

    // Show loading
    body.innerHTML = '<div style="text-align: center; padding: 2rem;"><p>Finding the perfect gifts...</p><div class="loading"></div></div>';
    nextBtn.disabled = true;
    nextBtn.classList.add('loading');

    console.log('[API] Showing loading state...');

    try {
        // Parse budget into structured format
        let budgetMax = null;
        let budgetMin = null;
        if (chatbotState.budget) {
            const parts = chatbotState.budget.split('_');
            if (parts[0] === 'under') {
                budgetMax = parseFloat(parts[1]);
            } else if (parts[1] === 'plus') {
                budgetMin = parseFloat(parts[0]);
            } else if (parts.length === 2) {
                budgetMin = parseFloat(parts[0]);
                budgetMax = parseFloat(parts[1]);
            }
        }

        // Prepare the wizard state
        const wizardState = {
            occasion: chatbotState.occasion,
            budget: chatbotState.budget || null,  // Keep for logging
            budget_max: budgetMax,
            budget_min: budgetMin,
            delivery_date: chatbotState.sameDayDelivery ? new Date().toISOString() : null,
            recipient_name: chatbotState.recipientName,
            recipient_loves: chatbotState.loves,
            recipient_hates: chatbotState.hates,
            recipient_allergies: chatbotState.allergies,
            recipient_dietary: chatbotState.allergies, // Using allergies as dietary too
            recipient_description: chatbotState.interests || null,
        };

        console.log('[API] Prepared wizard state:', wizardState);
        console.log('[API] Sending POST request to /api/recommendations...');

        // Call the backend API
        const response = await fetch('/api/recommendations', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(wizardState),
        });

        console.log('[API] Response received. Status:', response.status);

        if (!response.ok) {
            const errorText = await response.text();
            console.error('[API] Response error:', response.status, errorText);
            throw new Error(`API Error: ${response.status} - ${errorText}`);
        }

        const data = await response.json();
        console.log('[API] Response data:', data);

        // Close chatbot modal
        modal.classList.remove('show');
        nextBtn.disabled = false;
        nextBtn.classList.remove('loading');

        console.log('[API] Displaying recommendations...');

        // Display recommendations
        displayRecommendations(data.data);
    } catch (error) {
        console.error('[API] ERROR:', error);
        console.error('[API] Error stack:', error.stack);
        alert('Error getting recommendations. Check browser console (F12) for details.\n\n' + error.message);
        nextBtn.disabled = false;
        nextBtn.classList.remove('loading');
        body.innerHTML = '<p style="color: red;">Error loading recommendations. Please try again.\n\nCheck console (F12) for details.</p>';
    }
}

function displayRecommendations(recommendations) {
    const container = document.getElementById('recommendations-container');
    const grid = document.getElementById('recommendations-grid');
    const nameSpan = document.getElementById('recipient-name');

    console.log('[DISPLAY] displayRecommendations() called with:', recommendations);

    nameSpan.textContent = chatbotState.recipientName;

    grid.innerHTML = '';

    const picks = [
        { rec: recommendations.best_match, label: '🏆 Best Match' },
        { rec: recommendations.safe_bet, label: '✓ Safe Bet' },
        { rec: recommendations.unique, label: '⭐ Something Unique' },
    ];

    picks.forEach(({ rec, label }) => {
        if (!rec) return;

        console.log(`[DISPLAY] Processing ${label}:`, rec.product);
        console.log(`[DISPLAY]   - image_url: ${rec.product.image_url}`);
        console.log(`[DISPLAY]   - thumbnail_url: ${rec.product.thumbnail_url}`);
        console.log(`[DISPLAY]   - description length: ${rec.product.description?.length}`);

        const card = document.createElement('div');
        card.className = 'recommendation-card';

        // Determine fallback emoji if no image available
        const fallbackEmoji = rec.product.name.includes('chocolate')
            ? '🍫'
            : rec.product.name.includes('fruit')
                ? '🍓'
                : rec.product.name.includes('brownie')
                    ? '🧁'
                    : '🎁';

        // Create image placeholder container
        const imageContainer = document.createElement('div');
        imageContainer.className = 'rec-image-placeholder';

        // Use actual image if available
        const imageUrl = rec.product.image_url || rec.product.thumbnail_url;
        if (imageUrl) {
            const img = document.createElement('img');
            img.src = imageUrl;
            img.alt = rec.product.name;
            img.className = 'rec-image';
            img.onerror = function () {
                // If image fails to load, show emoji instead
                this.style.display = 'none';
                const emoji = document.createElement('div');
                emoji.style.fontSize = '3rem';
                emoji.style.display = 'flex';
                emoji.style.alignItems = 'center';
                emoji.style.justifyContent = 'center';
                emoji.style.height = '100%';
                emoji.textContent = fallbackEmoji;
                this.parentElement.appendChild(emoji);
            };
            imageContainer.appendChild(img);
        } else {
            // No image URL, show emoji
            const emoji = document.createElement('div');
            emoji.style.fontSize = '3rem';
            emoji.style.display = 'flex';
            emoji.style.alignItems = 'center';
            emoji.style.justifyContent = 'center';
            emoji.style.height = '100%';
            emoji.textContent = fallbackEmoji;
            imageContainer.appendChild(emoji);
        }

        // Create content section
        const content = document.createElement('div');
        content.className = 'rec-content';

        // Badge
        const badge = document.createElement('span');
        badge.className = 'rec-badge';
        badge.textContent = label;
        content.appendChild(badge);

        // Name
        const name = document.createElement('div');
        name.className = 'rec-name';
        name.textContent = rec.product.name;
        content.appendChild(name);

        // Price
        const price = document.createElement('div');
        price.className = 'rec-price';
        price.textContent = `$${rec.product.price.toFixed(2)}`;
        content.appendChild(price);

        // Description
        const description = document.createElement('div');
        description.className = 'rec-description';
        description.textContent = rec.product.description;
        content.appendChild(description);

        // Explanation
        const explanation = document.createElement('div');
        explanation.className = 'rec-explanation';
        explanation.textContent = rec.explanation;
        content.appendChild(explanation);

        // Actions
        const actions = document.createElement('div');
        actions.className = 'rec-actions';

        const selectBtn = document.createElement('button');
        selectBtn.className = 'btn-select';
        selectBtn.textContent = 'Select';
        selectBtn.onclick = () => selectProduct(rec.product.name, rec.product.price);
        actions.appendChild(selectBtn);

        const detailsBtn = document.createElement('button');
        detailsBtn.className = 'btn-details';
        detailsBtn.textContent = 'Details';
        actions.appendChild(detailsBtn);

        content.appendChild(actions);

        // Assemble card
        card.appendChild(imageContainer);
        card.appendChild(content);
        grid.appendChild(card);
    });

    container.classList.add('show');
}

function closeRecommendations() {
    document.getElementById('recommendations-container').classList.remove('show');
}

function selectProduct(name, price) {
    const pendingPersona = {
        name: chatbotState.recipientName || 'Recipient',
        birthday: null,
        loves: chatbotState.loves || [],
        hates: chatbotState.hates || [],
        allergies: chatbotState.allergies || [],
        dietary_restrictions: chatbotState.allergies || [],
        description: chatbotState.interests || null,
        last_gift: name,
    };

    localStorage.setItem('giftgenius_pending_persona', JSON.stringify(pendingPersona));

    const checkoutProduct = document.getElementById('checkout-product');
    checkoutProduct.innerHTML = `
        <div class="checkout-product-name">${name}</div>
        <div class="checkout-product-price">$${price.toFixed(2)}</div>
    `;

    document.getElementById('recommendations-container').classList.remove('show');
    document.getElementById('checkout-page').classList.add('show');
}

function goBackToRecommendations() {
    document.getElementById('checkout-page').classList.remove('show');
    document.getElementById('signup-page').classList.remove('show');
    document.getElementById('recommendations-container').classList.add('show');
}

// Initialize on load
document.addEventListener('DOMContentLoaded', initChatbot);
