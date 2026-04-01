const API_BASE_URL = "/api";

let currentUser = null;
let selectedPlan = null;
let tg = window.Telegram.WebApp;

async function initializeApp() {
    tg.ready();
    
    tg.MainButton.hide();
    
    const verifyBtn = document.getElementById("verify-btn");
    verifyBtn.addEventListener("click", handleVerification);
    
    tg.MainButton.onClick(purchasePlan);
    
    await loadPlans();
}

async function handleVerification() {
    showLoading(true);
    const authError = document.getElementById("auth-error");
    authError.style.display = "none";
    
    try {
        const initData = tg.initData;
        
        if (!initData) {
            throw new Error("Unable to get Telegram data");
        }
        
        const response = await fetch(`${API_BASE_URL}/auth/verify`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                init_data: initData,
            }),
        });
        
        if (!response.ok) {
            let errorMessage = "Verification failed";
            try {
                const errorData = await response.json();
                errorMessage = errorData.detail || errorData.message || errorMessage;
            } catch (e) {
                errorMessage = `HTTP ${response.status}: ${response.statusText}`;
            }
            throw new Error(errorMessage);
        }
        
        currentUser = await response.json();
        
        displayUserInfo();
        document.getElementById("auth-section").style.display = "none";
        document.getElementById("plans-section").style.display = "block";
        document.getElementById("subscriptions-section").style.display = "block";
        
        await loadUserSubscriptions();
    } catch (error) {
        const errorMessage = error instanceof Error ? error.message : String(error);
        authError.textContent = errorMessage;
        authError.style.display = "block";
        console.error("Verification error:", error);
    } finally {
        showLoading(false);
    }
}

function displayUserInfo() {
    const userInfo = document.getElementById("user-info");
    const userName = document.getElementById("user-name");
    const premiumBadge = document.getElementById("premium-badge");
    
    userInfo.style.display = "flex";
    userName.textContent = `${currentUser.first_name} ${currentUser.last_name || ""}`.trim();
    
    if (currentUser.is_premium) {
        premiumBadge.style.display = "inline-block";
    }
}

async function loadPlans() {
    try {
        const response = await fetch(`${API_BASE_URL}/subscriptions/plans`);
        
        if (!response.ok) {
            throw new Error("Failed to load plans");
        }
        
        const plans = await response.json();
        displayPlans(plans);
    } catch (error) {
        console.error("Error loading plans:", error);
    }
}

function displayPlans(plans) {
    const container = document.getElementById("plans-container");
    container.innerHTML = "";
    
    plans.forEach((plan, index) => {
        const planCard = document.createElement("div");
        planCard.className = "plan-card";
        
        if (index === 0) {
            planCard.classList.add("featured");
        }
        
        const features = plan.features.split(",").map(f => f.trim());
        
        planCard.innerHTML = `
            <div class="plan-header">
                <div class="plan-name">${plan.name}</div>
                <div class="plan-price">$${plan.price.toFixed(2)}</div>
            </div>
            <div class="plan-duration">${plan.duration_days} days</div>
            <div class="plan-description">${plan.description}</div>
            <ul class="plan-features">
                ${features.map(f => `<li>${f}</li>`).join("")}
            </ul>
        `;
        
        planCard.addEventListener("click", () => selectPlan(plan, planCard));
        container.appendChild(planCard);
    });
}

function selectPlan(plan, planCard) {
    if (!currentUser) {
        alert("Please verify your account first");
        return;
    }
    
    const allCards = document.querySelectorAll(".plan-card");
    allCards.forEach(card => card.classList.remove("selected"));
    
    planCard.classList.add("selected");
    selectedPlan = plan;
    
    tg.MainButton.setText(`Buy ${plan.name} for $${plan.price.toFixed(2)}`);
    tg.MainButton.show();
}

async function purchasePlan() {
    if (!currentUser || !selectedPlan) {
        alert("Please select a plan first");
        return;
    }
    
    tg.MainButton.showProgress();
    
    try {
        const response = await fetch(`${API_BASE_URL}/subscriptions/purchase`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                user_id: currentUser.id,
                plan_id: selectedPlan.id,
            }),
        });
        
        if (!response.ok) {
            let errorMessage = "Subscription failed";
            try {
                const errorData = await response.json();
                errorMessage = errorData.detail || errorData.message || errorMessage;
            } catch (e) {
                errorMessage = `HTTP ${response.status}: ${response.statusText}`;
            }
            throw new Error(errorMessage);
        }
        
        const subscription = await response.json();
        
        currentUser.is_premium = true;
        displayUserInfo();
        
        document.getElementById("plans-section").style.display = "none";
        await loadUserSubscriptions();
        
        tg.MainButton.hideProgress();
        tg.MainButton.hide();
        selectedPlan = null;
        
        alert(`Subscription to ${subscription.plan_name} successful!`);
    } catch (error) {
        tg.MainButton.hideProgress();
        const errorMessage = error instanceof Error ? error.message : String(error);
        alert(`Error: ${errorMessage}`);
        console.error("Subscription error:", error);
    }
}

async function loadUserSubscriptions() {
    if (!currentUser) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/subscriptions/user/${currentUser.id}`);
        
        if (!response.ok) {
            throw new Error("Failed to load subscriptions");
        }
        
        const subscriptions = await response.json();
        displaySubscriptions(subscriptions);
    } catch (error) {
        console.error("Error loading subscriptions:", error);
    }
}

function displaySubscriptions(subscriptions) {
    const container = document.getElementById("subscriptions-container");
    
    if (subscriptions.length === 0) {
        container.innerHTML = "<p>No active subscriptions</p>";
        return;
    }
    
    container.innerHTML = "";
    
    subscriptions.forEach(sub => {
        const subItem = document.createElement("div");
        subItem.className = "subscription-item";
        
        const expiresDate = new Date(sub.expires_at);
        const formattedDate = expiresDate.toLocaleDateString("en-US", {
            year: "numeric",
            month: "long",
            day: "numeric",
        });
        
        subItem.innerHTML = `
            <div class="subscription-header">
                <div class="subscription-name">${sub.plan_name}</div>
                <div class="subscription-status">${sub.is_active ? "Active" : "Inactive"}</div>
            </div>
            <div class="subscription-details">
                <p>Price: $${sub.price.toFixed(2)}</p>
                <p>Duration: ${sub.duration_days} days</p>
            </div>
            <div class="subscription-expires">
                Expires: ${formattedDate}
            </div>
        `;
        
        container.appendChild(subItem);
    });
}

function showLoading(show) {
    const loading = document.getElementById("loading");
    loading.style.display = show ? "flex" : "none";
}

document.addEventListener("DOMContentLoaded", initializeApp);
