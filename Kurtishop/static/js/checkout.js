let currentStep = 1;

function updateProgress(step) {
    document.querySelectorAll(".step").forEach(stepItem => {
        const number = parseInt(stepItem.dataset.step);
        const circle = stepItem.querySelector("div");

        if (number <= step) {
            stepItem.classList.remove("text-gray-400");
            stepItem.classList.add("text-red-600");
            circle.classList.remove("border-gray-300");
            circle.classList.add("border-red-600");
        } else {
            stepItem.classList.remove("text-red-600");
            stepItem.classList.add("text-gray-400");
            circle.classList.remove("border-red-600");
            circle.classList.add("border-gray-300");
        }
    });
}

function showStep(step) {
    document.querySelectorAll(".step-content").forEach(content => {
        content.classList.add("hidden");
    });

    const targetStep = document.getElementById(`step-${step}`);
    if (targetStep) {
        targetStep.classList.remove("hidden");
    }

    currentStep = step;
    updateProgress(step);
}

// ==================== VALIDATION HELPERS ====================

function showError(input, message) {
    // Remove old error
    let errorEl = input.parentElement.querySelector('.error-msg');
    if (errorEl) errorEl.remove();

    // Create new error
    errorEl = document.createElement('p');
    errorEl.className = 'mt-1 text-xs text-red-600 error-msg';
    errorEl.textContent = message;
    input.parentElement.appendChild(errorEl);
    
    input.classList.add('border-red-600', 'focus:ring-red-500');
}

function clearError(input) {
    const errorEl = input.parentElement.querySelector('.error-msg');
    if (errorEl) errorEl.remove();
    input.classList.remove('border-red-600', 'focus:ring-red-500');
}

function validateEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function validatePhone(phone) {
    // Indian phone number (10 digits, optional +91 or 0)
    const cleaned = phone.replace(/[\s\-\(\)]/g, '');
    return /^[6-9]\d{9}$/.test(cleaned) || /^\+91[6-9]\d{9}$/.test(cleaned);
}

function validateRequired(value) {
    return value && value.trim().length > 0;
}

// Main validation for a step
function validateStep(step) {
    let isValid = true;

    if (step === 1) { // Contact Information
        const fullName = document.querySelector('input[name="full_name"]');
        const email = document.querySelector('input[name="email"]');
        const phone = document.querySelector('input[name="phone"]');

        // Full Name
        if (!validateRequired(fullName.value)) {
            showError(fullName, "Full name is required");
            isValid = false;
        } else if (fullName.value.trim().length < 2) {
            showError(fullName, "Name must be at least 2 characters");
            isValid = false;
        } else {
            clearError(fullName);
        }

        // Email
        if (!validateRequired(email.value)) {
            showError(email, "Email address is required");
            isValid = false;
        } else if (!validateEmail(email.value)) {
            showError(email, "Please enter a valid email address");
            isValid = false;
        } else {
            clearError(email);
        }

        // Phone
        if (!validateRequired(phone.value)) {
            showError(phone, "Phone number is required");
            isValid = false;
        } else if (!validatePhone(phone.value)) {
            showError(phone, "Please enter a valid 10-digit Indian phone number");
            isValid = false;
        } else {
            clearError(phone);
        }
    }

    else if (step === 2) { // Shipping Address
        const fields = [
            { name: 'address_line_1', label: 'Address Line 1' },
            { name: 'city', label: 'City' },
            { name: 'state', label: 'State' },
            { name: 'postal_code', label: 'Postal Code' },
            { name: 'country', label: 'Country' }
        ];

        fields.forEach(field => {
            const input = document.querySelector(`input[name="${field.name}"], select[name="${field.name}"]`);
            if (input) {
                if (!validateRequired(input.value)) {
                    showError(input, `${field.label} is required`);
                    isValid = false;
                } else {
                    clearError(input);
                }
            }
        });

        // Optional: Postal code format (6 digits for India)
        const postal = document.querySelector('input[name="postal_code"]');
        if (postal && validateRequired(postal.value)) {
            if (!/^\d{6}$/.test(postal.value.trim())) {
                showError(postal, "Postal code must be 6 digits");
                isValid = false;
            }
        }
    }

    return isValid;
}

// ==================== STEP NAVIGATION ====================

function nextStep(next) {
    if (validateStep(currentStep)) {
        showStep(next);
    }
}

function prevStep(prev) {
    showStep(prev);
}

// Form submission validation (final safety net)
function handleSubmit(e) {
    if (!validateStep(1) || !validateStep(2)) {
        e.preventDefault();
        showStep(1); // Go back to first invalid step
        alert("Please fix the errors in the form before submitting.");
    }
}

// ==================== INIT ====================

document.addEventListener("DOMContentLoaded", function () {
    const config = window.checkoutConfig;
    if (!config) return;

    // Show correct starting step
    showStep(config.triggerPayment ? 3 : 1);

    // Attach real-time validation on input
    const allInputs = document.querySelectorAll('#checkout-form input, #checkout-form select, #checkout-form textarea');
    allInputs.forEach(input => {
        input.addEventListener('blur', () => {
            // Re-validate current step on blur
            validateStep(currentStep);
        });
    });

    // Prevent default next buttons if validation fails (already handled in nextStep)

    // Final form submit validation
    const form = document.getElementById('checkout-form');
    if (form) {
        form.addEventListener('submit', handleSubmit);
    }

    // Razorpay payment flow
    if (config.triggerPayment) {
        const options = {
            key: config.razorpayKey,
            amount: config.amount,
            currency: "INR",
            order_id: config.razorpayOrderId,
            name: "Liara",
            description: `Order #${config.orderNumber}`,
            prefill: config.customer,
            theme: { color: "#C1121F" },

            handler(response) {
                fetch(config.verifyUrl, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": config.csrfToken
                    },
                    body: JSON.stringify({
                        razorpay_payment_id: response.razorpay_payment_id,
                        razorpay_order_id: response.razorpay_order_id,
                        razorpay_signature: response.razorpay_signature,
                        order_number: config.orderNumber
                    })
                })
                .then(res => res.json())
                .then(data => {
                    if (data.status === "success") {
                        window.location.href = data.redirect_url;
                    } else {
                        alert("Payment verification failed.");
                    }
                })
                .catch(() => alert("Something went wrong."));
            }
        };

        const rzp = new Razorpay(options);
        rzp.open();
    }
});