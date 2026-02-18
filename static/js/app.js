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

    // Show success message
    const signupContent = document.getElementById('signup-page').querySelector('.signup-content');
    signupContent.innerHTML = `
        <div style="text-align: center; padding: 2rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🎉</div>
            <h2>Welcome to Gift Genius!</h2>
            <p>Your account has been created successfully.</p>
            <p style="color: var(--text-color); margin-top: 1rem;">We'll send you email reminders for upcoming occasions.</p>
            <p style="color: var(--text-color);">Check your email for confirmation.</p>
            <button class="btn-primary" style="margin-top: 2rem;" onclick="completeFlow()">Done</button>
        </div>
    `;
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
