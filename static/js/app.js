const STORAGE_KEYS = {
    user: 'giftgenius_user',
    pendingPersona: 'giftgenius_pending_persona',
};

function getCurrentUser() {
    const raw = localStorage.getItem(STORAGE_KEYS.user);
    if (!raw) return null;
    try {
        return JSON.parse(raw);
    } catch (err) {
        return null;
    }
}

function setCurrentUser(user) {
    localStorage.setItem(STORAGE_KEYS.user, JSON.stringify(user));
    syncLoginButton();
}

function clearPendingPersona() {
    localStorage.removeItem(STORAGE_KEYS.pendingPersona);
}

function getPendingPersona() {
    const raw = localStorage.getItem(STORAGE_KEYS.pendingPersona);
    if (!raw) return null;
    try {
        return JSON.parse(raw);
    } catch (err) {
        return null;
    }
}

function syncLoginButton() {
    const loginBtn = document.getElementById('login-btn');
    const user = getCurrentUser();
    if (!loginBtn) return;
    loginBtn.textContent = user ? 'My Account' : 'Login';
}

function openLogin() {
    document.getElementById('login-page').classList.add('show');
}

function closeLogin() {
    document.getElementById('login-page').classList.remove('show');
}

function openAccount() {
    const loginPage = document.getElementById('login-page');
    const signupPage = document.getElementById('signup-page');
    if (loginPage) loginPage.classList.remove('show');
    if (signupPage) signupPage.classList.remove('show');
    document.getElementById('account-page').classList.add('show');
    loadAccount();
}

function closeAccount() {
    document.getElementById('account-page').classList.remove('show');
}

function openInbox() {
    const accountPage = document.getElementById('account-page');
    if (accountPage) accountPage.classList.remove('show');
    document.getElementById('email-inbox-page').classList.add('show');
    loadInbox();
}

function closeInbox() {
    document.getElementById('email-inbox-page').classList.remove('show');
}

window.closeLogin = closeLogin;
window.closeAccount = closeAccount;
window.closeInbox = closeInbox;
window.openAccount = openAccount;

function listToInput(list) {
    return (list || []).join(', ');
}

function parseListInput(value) {
    return value
        .split(',')
        .map((item) => item.trim())
        .filter(Boolean);
}

async function apiLogin(payload) {
    const response = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
    });
    if (!response.ok) {
        throw new Error('Login failed');
    }
    return response.json();
}

async function apiGetPersonas(userId) {
    const response = await fetch(`/api/personas?user_id=${encodeURIComponent(userId)}`);
    if (!response.ok) {
        throw new Error('Failed to load personas');
    }
    return response.json();
}

async function apiCreatePersona(payload) {
    const response = await fetch('/api/personas', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
    });
    if (!response.ok) {
        throw new Error('Failed to create persona');
    }
    return response.json();
}

async function apiUpdatePersona(personaId, payload) {
    const response = await fetch(`/api/personas/${personaId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
    });
    if (!response.ok) {
        throw new Error('Failed to update persona');
    }
    return response.json();
}

async function apiDeletePersona(personaId) {
    const response = await fetch(`/api/personas/${personaId}`, {
        method: 'DELETE',
    });
    if (!response.ok) {
        throw new Error('Failed to delete persona');
    }
    return response.json();
}

async function triggerReminders(userEmail) {
    if (!userEmail) return;
    await fetch('/api/reminders/check', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_email: userEmail }),
    });
}

async function loadAccount(activeId) {
    const user = getCurrentUser();
    if (!user) {
        openLogin();
        return;
    }

    const tabs = document.getElementById('persona-tabs');
    const details = document.getElementById('persona-details');
    tabs.innerHTML = '';
    details.innerHTML = '<p>Loading personas...</p>';

    let personas = [];
    try {
        const data = await apiGetPersonas(user.user_id);
        personas = data.personas || [];
    } catch (err) {
        details.innerHTML = '<p>Failed to load personas. Please try again.</p>';
        return;
    }

    if (personas.length === 0) {
        details.innerHTML = '<p>No personas yet. Add your first person.</p>';
        return;
    }

    const selectedId = activeId || personas[0].id;

    personas.forEach((persona) => {
        const button = document.createElement('button');
        button.className = 'persona-tab' + (persona.id === selectedId ? ' active' : '');
        button.textContent = persona.name;
        button.addEventListener('click', () => loadAccount(persona.id));
        tabs.appendChild(button);
    });

    const selected = personas.find((p) => p.id === selectedId) || personas[0];
    renderPersonaDetails(selected);
}

function renderPersonaDetails(persona) {
    const details = document.getElementById('persona-details');
    if (!details) return;

    details.innerHTML = `
        <h3>${persona.name}</h3>
        <div class="form-group">
            <label>Birthday</label>
            <input id="persona-birthday" type="date" value="${persona.birthday || ''}">
        </div>
        <div class="form-group">
            <label>Loves (comma separated)</label>
            <input id="persona-loves" type="text" value="${listToInput(persona.loves)}">
        </div>
        <div class="form-group">
            <label>Hates (comma separated)</label>
            <input id="persona-hates" type="text" value="${listToInput(persona.hates)}">
        </div>
        <div class="form-group">
            <label>Allergies (comma separated)</label>
            <input id="persona-allergies" type="text" value="${listToInput(persona.allergies)}">
        </div>
        <div class="form-group">
            <label>Dietary Restrictions (comma separated)</label>
            <input id="persona-dietary" type="text" value="${listToInput(persona.dietary_restrictions)}">
        </div>
        <div class="form-group">
            <label>Notes</label>
            <textarea id="persona-description" rows="3">${persona.description || ''}</textarea>
        </div>
        <div class="checkbox-group">
            <input id="persona-reminders" type="checkbox" ${persona.email_reminders ? 'checked' : ''}>
            <label for="persona-reminders">Email reminders enabled</label>
        </div>
        <div class="persona-actions">
            <button id="save-persona" class="btn-primary">Save</button>
            <button id="delete-persona" class="btn-secondary">Delete</button>
        </div>
    `;

    document.getElementById('save-persona').addEventListener('click', async () => {
        const updates = {
            birthday: document.getElementById('persona-birthday').value || null,
            loves: parseListInput(document.getElementById('persona-loves').value),
            hates: parseListInput(document.getElementById('persona-hates').value),
            allergies: parseListInput(document.getElementById('persona-allergies').value),
            dietary_restrictions: parseListInput(document.getElementById('persona-dietary').value),
            description: document.getElementById('persona-description').value || null,
            email_reminders: document.getElementById('persona-reminders').checked,
        };
        await apiUpdatePersona(persona.id, updates);
        const user = getCurrentUser();
        if (user) {
            await triggerReminders(user.email);
        }
        await loadAccount(persona.id);
    });

    document.getElementById('delete-persona').addEventListener('click', async () => {
        const confirmed = confirm('Delete this persona?');
        if (!confirmed) return;
        await apiDeletePersona(persona.id);
        await loadAccount();
    });
}

function renderNewPersonaForm() {
    const details = document.getElementById('persona-details');
    details.innerHTML = `
        <h3>Add New Person</h3>
        <div class="form-group">
            <label>Name</label>
            <input id="new-name" type="text" placeholder="Full name">
        </div>
        <div class="form-group">
            <label>Birthday</label>
            <input id="new-birthday" type="date">
        </div>
        <div class="form-group">
            <label>Loves (comma separated)</label>
            <input id="new-loves" type="text">
        </div>
        <div class="form-group">
            <label>Hates (comma separated)</label>
            <input id="new-hates" type="text">
        </div>
        <div class="form-group">
            <label>Allergies (comma separated)</label>
            <input id="new-allergies" type="text">
        </div>
        <div class="form-group">
            <label>Dietary Restrictions (comma separated)</label>
            <input id="new-dietary" type="text">
        </div>
        <div class="form-group">
            <label>Notes</label>
            <textarea id="new-description" rows="3"></textarea>
        </div>
        <div class="checkbox-group">
            <input id="new-reminders" type="checkbox" checked>
            <label for="new-reminders">Email reminders enabled</label>
        </div>
        <div class="persona-actions">
            <button id="create-persona" class="btn-primary">Create</button>
        </div>
    `;

    document.getElementById('create-persona').addEventListener('click', async () => {
        const user = getCurrentUser();
        if (!user) {
            openLogin();
            return;
        }
        const name = document.getElementById('new-name').value.trim();
        if (!name) {
            alert('Please enter a name');
            return;
        }
        const payload = {
            user_id: user.user_id,
            name,
            birthday: document.getElementById('new-birthday').value || null,
            loves: parseListInput(document.getElementById('new-loves').value),
            hates: parseListInput(document.getElementById('new-hates').value),
            allergies: parseListInput(document.getElementById('new-allergies').value),
            dietary_restrictions: parseListInput(document.getElementById('new-dietary').value),
            description: document.getElementById('new-description').value || null,
            email_reminders: document.getElementById('new-reminders').checked,
        };
        const result = await apiCreatePersona(payload);
        await triggerReminders(user.email);
        await loadAccount(result.persona.id);
    });
}

async function loadInbox() {
    const user = getCurrentUser();
    const inbox = document.getElementById('inbox-list');
    if (!user) {
        inbox.innerHTML = '<p>Please log in to view your inbox.</p>';
        return;
    }
    const response = await fetch(`/api/inbox?user_email=${encodeURIComponent(user.email)}`);
    const data = await response.json();
    const messages = data.messages || [];
    if (messages.length === 0) {
        inbox.innerHTML = '<p>No emails yet.</p>';
        return;
    }
    inbox.innerHTML = '';
    messages.forEach((message) => {
        const item = document.createElement('div');
        item.className = 'inbox-item';
        item.innerHTML = `
            <h4>${message.subject}</h4>
            <p>${message.body.replace(/\n/g, '<br>')}</p>
            <small>${message.sent_at}</small>
        `;
        inbox.appendChild(item);
    });
}

async function savePendingPersona(user) {
    const pending = getPendingPersona();
    if (!pending) return;

    const payload = {
        user_id: user.user_id,
        name: pending.name,
        birthday: pending.birthday || null,
        loves: pending.loves || [],
        hates: pending.hates || [],
        allergies: pending.allergies || [],
        dietary_restrictions: pending.dietary_restrictions || [],
        description: pending.description || null,
        email_reminders: true,
    };

    await apiCreatePersona(payload);
    await triggerReminders(user.email);
    clearPendingPersona();
}

// Handle Checkout Form
document.addEventListener('DOMContentLoaded', function () {
    const checkoutForm = document.getElementById('checkout-form');
    if (checkoutForm) {
        checkoutForm.addEventListener('submit', function (e) {
            e.preventDefault();
            completeCheckout();
        });
    }

    const signupForm = document.getElementById('signup-form');
    if (signupForm) {
        signupForm.addEventListener('submit', function (e) {
            e.preventDefault();
            completeSignup();
        });
    }

    const loginBtn = document.getElementById('login-btn');
    if (loginBtn) {
        loginBtn.addEventListener('click', () => {
            const user = getCurrentUser();
            if (user) {
                openAccount();
            } else {
                openLogin();
            }
        });
    }

    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(loginForm);
            const fullName = formData.get('full_name');
            const email = formData.get('email');
            if (!fullName || !email) {
                alert('Please fill in all fields');
                return;
            }
            const user = await apiLogin({ full_name: fullName, email });
            setCurrentUser(user);
            closeLogin();
            openAccount();
        });
    }

    const openInboxBtn = document.getElementById('open-inbox');
    if (openInboxBtn) {
        openInboxBtn.addEventListener('click', () => {
            openInbox();
        });
    }

    const addPersonaBtn = document.getElementById('add-persona');
    if (addPersonaBtn) {
        addPersonaBtn.addEventListener('click', () => {
            renderNewPersonaForm();
        });
    }

    syncLoginButton();
});

function completeCheckout() {
    const checkoutForm = document.getElementById('checkout-form');
    const formData = new FormData(checkoutForm);

    // Validate form
    let isValid = true;
    formData.forEach((value) => {
        if (!value.trim()) {
            isValid = false;
        }
    });

    if (!isValid) {
        alert('Please fill in all fields');
        return;
    }

    // Show success message with animation
    const checkoutPage = document.getElementById('checkout-page');
    const checkoutContent = checkoutPage.querySelector('.checkout-content');

    checkoutContent.innerHTML = `
        <div style="text-align: center; padding: 2rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">✓</div>
            <h2>Order Confirmed!</h2>
            <p>Thank you for your order. Your gift will be delivered soon.</p>
            <p style="color: var(--text-color); margin-top: 1rem;">Order confirmation has been sent to your email.</p>
            <button class="btn-primary" style="margin-top: 2rem;" onclick="showSignupAfterCheckout()">Continue</button>
        </div>
    `;
}

function showSignupAfterCheckout() {
    document.getElementById('checkout-page').classList.remove('show');
    showSignupPage();
}

function showSignupPage() {
    document.getElementById('signup-page').classList.add('show');
}

function completeSignup() {
    const signupForm = document.getElementById('signup-form');
    const formData = new FormData(signupForm);

    // Validate form
    const fullName = formData.get('full_name');
    const email = formData.get('email');
    const password = formData.get('password');

    if (!fullName || !email || !password) {
        alert('Please fill in all fields');
        return;
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        alert('Please enter a valid email');
        return;
    }

    // Password validation
    if (password.length < 6) {
        alert('Password must be at least 6 characters');
        return;
    }

    const proceed = async () => {
        try {
            const user = await apiLogin({ full_name: fullName, email });
            setCurrentUser(user);
            await savePendingPersona(user);

            const signupContent = document.getElementById('signup-page').querySelector('.signup-content');
            signupContent.innerHTML = `
                <div style="text-align: center; padding: 2rem;">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">🎉</div>
                    <h2>Welcome to Gift Genius!</h2>
                    <p>Your account has been created successfully.</p>
                    <p style="color: var(--text-color); margin-top: 1rem;">We'll send you email reminders for upcoming occasions.</p>
                    <p style="color: var(--text-color);">Check your email for confirmation.</p>
                    <button class="btn-primary" style="margin-top: 2rem;" onclick="openAccount()">View My People</button>
                    <button class="btn-secondary" style="margin-top: 1rem;" onclick="completeFlow()">Done</button>
                </div>
            `;
        } catch (err) {
            alert('Signup failed. Please try again.');
        }
    };

    proceed();
}

function completeFlow() {
    // Close all modals
    document.getElementById('signup-page').classList.remove('show');
    document.getElementById('checkout-page').classList.remove('show');
    document.getElementById('recommendations-container').classList.remove('show');
    document.getElementById('chatbot-modal').classList.remove('show');

    // Reset chatbot state
    chatbotState.currentStep = 0;
    chatbotState.occasion = '';
    chatbotState.budget = '';
    chatbotState.sameDayDelivery = false;
    chatbotState.recipientName = '';
    chatbotState.loves = [];
    chatbotState.hates = [];
    chatbotState.allergies = [];
    chatbotState.interests = '';

    clearPendingPersona();

    // Show completion message
    showCompletionMessage();
}

function showCompletionMessage() {
    const message = document.createElement('div');
    message.className = 'completion-modal';
    message.innerHTML = `
        <div class="completion-content">
            <div style="text-align: center;">
                <div style="font-size: 4rem; margin-bottom: 1rem;">🎁</div>
                <h2>Thank You for Using Gift Genius!</h2>
                <p>Your recipient will love their gift!</p>
                <button class="btn-primary" style="margin-top: 2rem;" onclick="this.parentElement.parentElement.remove()">Back to Home</button>
            </div>
        </div>
    `;

    message.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.5);
        z-index: 3000;
        display: flex;
        align-items: center;
        justify-content: center;
        animation: fadeIn 0.3s ease;
    `;

    const content = message.querySelector('div');
    content.style.cssText = `
        background-color: white;
        padding: 3rem 2rem;
        border-radius: 12px;
        max-width: 500px;
        box-shadow: var(--shadow-lg);
        animation: slideUp 0.3s ease;
    `;

    document.body.appendChild(message);
}

// Responsive drawer for mobile
window.addEventListener('resize', function () {
    const width = window.innerWidth;
    const modals = document.querySelectorAll('.modal-content, .recommendations-content');

    if (width < 768) {
        modals.forEach((modal) => {
            modal.style.maxHeight = '95vh';
        });
    }
});

// Add keyboard shortcuts
document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
        const modal = document.getElementById('chatbot-modal');
        const recommendations = document.getElementById('recommendations-container');

        if (modal.classList.contains('show')) {
            modal.classList.remove('show');
        } else if (recommendations.classList.contains('show')) {
            closeRecommendations();
        }
    }
});
