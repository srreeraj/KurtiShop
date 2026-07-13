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

    document
        .getElementById(`step-${step}`)
        .classList.remove("hidden");

    currentStep = step;

    updateProgress(step);
}

function nextStep(step) {
    showStep(step);
}

function prevStep(step) {
    showStep(step);
}

document.addEventListener("DOMContentLoaded", function () {

   const config = window.checkoutConfig;

    if (!config) {
        return;
    }

    showStep(config.triggerPayment ? 3 : 1);

    if (!config.triggerPayment) return;

    const options = {

        key: config.razorpayKey,
        amount: config.amount,
        currency: "INR",
        order_id: config.razorpayOrderId,

        name: "Liara",

        description: `Order #${config.orderNumber}`,

        prefill: config.customer,

        theme: {
            color: "#C1121F"
        },

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
            .catch(() => {

                alert("Something went wrong.");

            });

        }

    };

    const rzp = new Razorpay(options);

    rzp.open();

});