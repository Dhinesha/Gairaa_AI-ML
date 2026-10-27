// ===== EMOJI MAP for features =====
const FEATURE_EMOJI = {
    'quantity': '📦',
    'unit_price': '💰',
    'unit price': '💰',
    'discount': '🏷️',
    'shipping_cost': '🚚',
    'shipping cost': '🚚',
    'region': '🌍',
    'category': '🛍️',
    'customer_type': '👤',
    'customer type': '👤',
    'payment_method': '💳',
    'payment method': '💳',
};

function getEmoji(featureName) {
    const lower = featureName.toLowerCase();
    for (const [key, emoji] of Object.entries(FEATURE_EMOJI)) {
        if (lower.includes(key)) return emoji;
    }
    return '📊';
}

function getCleanName(featureName) {
    // Convert technical names to readable names
    return featureName
        .replace(/\b(Customer Type|Category|Region|Payment Method)\s*=?\s*/gi, (match) => match.trim() + ' ')
        .replace(/_/g, ' ')
        .replace(/\s+/g, ' ')
        .trim();
}

// ===== FORM SUBMIT =====
document.getElementById('prediction-form').addEventListener('submit', async function(e) {
    e.preventDefault();

    const errorEl = document.getElementById('error-message');
    errorEl.classList.add('hidden');
    document.getElementById('empty-state').classList.add('hidden');
    document.getElementById('result-content').classList.add('hidden');
    document.getElementById('loading').classList.remove('hidden');

    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());

    data.quantity = parseInt(data.quantity);
    data.unit_price = parseFloat(data.unit_price);
    data.discount = parseFloat(data.discount);
    data.shipping_cost = parseFloat(data.shipping_cost);

    try {
        const response = await fetch('http://127.0.0.1:8000/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || "Prediction failed");
        }

        const result = await response.json();
        displayResult(result, data);
    } catch (error) {
        errorEl.textContent = `❌ ${error.message}`;
        errorEl.classList.remove('hidden');
        document.getElementById('loading').classList.add('hidden');
        document.getElementById('empty-state').classList.remove('hidden');
    }
});

// ===== DISPLAY RESULT =====
function displayResult(result, inputData) {
    document.getElementById('loading').classList.add('hidden');
    document.getElementById('result-content').classList.remove('hidden');

    const isHigh = result.prediction === 'HIGH SALES';
    const probPct = (result.probability * 100).toFixed(1);

    // --- 1. Prediction Badge ---
    const predClassEl = document.getElementById('pred-class');
    predClassEl.textContent = result.prediction;
    predClassEl.className = `pred-badge ${isHigh ? 'high-sales' : 'low-sales'}`;

    // Prediction card border glow
    const predCard = document.getElementById('prediction-card');
    predCard.style.borderColor = isHigh ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.2)';

    // --- 2. Confidence Gauge ---
    const confFill = document.getElementById('confidence-fill');
    const confValue = document.getElementById('confidence-value');
    const confPct = isHigh ? probPct : (100 - parseFloat(probPct)).toFixed(1);

    setTimeout(() => {
        confFill.style.width = `${confPct}%`;
        confFill.className = `confidence-bar-fill ${parseFloat(confPct) < 55 ? 'low-conf' : ''}`;
    }, 100);
    confValue.textContent = `${confPct}%`;

    // --- 3. Story (Simple Explanation) ---
    buildStory(result, inputData, isHigh, probPct);

    // --- 4. Visual Factor Cards ---
    buildFactorCards(result.explanation);

    // --- 5. Actionable Suggestions ---
    buildSuggestions(result.explanation, isHigh, inputData);

    // --- 6. Technical SHAP Chart ---
    buildShapChart(result.explanation);
}

// ===== BUILD STORY =====
function buildStory(result, inputData, isHigh, probPct) {
    const storyEl = document.getElementById('story-text');
    const he = result.human_explanation;

    // Find top positive and negative factors
    const topPositive = result.explanation.filter(e => e.shap_value > 0).sort((a, b) => b.shap_value - a.shap_value);
    const topNegative = result.explanation.filter(e => e.shap_value < 0).sort((a, b) => a.shap_value - b.shap_value);

    let confWord;
    if (parseFloat(probPct) > 75 || parseFloat(probPct) < 25) confWord = 'very confident';
    else if (parseFloat(probPct) > 60 || parseFloat(probPct) < 40) confWord = 'moderately confident';
    else confWord = 'not very confident (close call!)';

    let storyHtml = `<p>`;
    storyHtml += `The AI looked at your transaction and predicted `;
    storyHtml += `<span class="story-highlight ${isHigh ? 'good' : 'bad'}">${result.prediction}</span>. `;
    storyHtml += `It is <span class="story-highlight neutral">${confWord}</span> about this decision.</p>`;

    storyHtml += `<p style="margin-top: 0.75rem">`;
    if (topPositive.length > 0) {
        const top = topPositive[0];
        storyHtml += `The <strong>#1 reason pushing toward High Sales</strong> is that `;
        storyHtml += describeFactorSimple(top, inputData) + '. ';
    }

    if (topNegative.length > 0) {
        const top = topNegative[0];
        storyHtml += `On the other hand, the <strong>#1 reason pulling toward Low Sales</strong> is that `;
        storyHtml += describeFactorSimple(top, inputData) + '.';
    }
    storyHtml += `</p>`;

    // Analogy
    if (isHigh && topPositive.length > 0) {
        storyHtml += `<div class="story-analogy"><strong>🧠 Think of it like this:</strong> Even though some factors (like discount or shipping cost) are working against the sale, the sheer volume of items being purchased is strong enough to tip the scale toward a high-value transaction.</div>`;
    } else if (!isHigh && topNegative.length > 0) {
        storyHtml += `<div class="story-analogy"><strong>🧠 Think of it like this:</strong> While some factors help, the combination of pricing, discounts, or lower quantities means the overall transaction value is likely to fall in the lower range.</div>`;
    }

    storyEl.innerHTML = storyHtml;
}

function describeFactorSimple(factor, inputData) {
    const name = factor.feature.toLowerCase();
    const val = factor.value;

    if (name.includes('quantity')) return `you're selling <strong>${val} items</strong> (more items = more revenue)`;
    if (name.includes('unit price')) return `the unit price is <strong>₹${val}</strong>`;
    if (name.includes('discount')) return `there's a <strong>${val}% discount</strong> (discounts reduce revenue)`;
    if (name.includes('shipping')) return `shipping costs are <strong>₹${val}</strong>`;
    if (name.includes('region')) return `the sale is in the <strong>${val}</strong> region`;
    if (name.includes('category')) return `the product category is <strong>${val}</strong>`;
    if (name.includes('customer')) return `the customer type is <strong>${val.replace('type_', '')}</strong>`;
    if (name.includes('payment')) return `payment is via <strong>${val.replace('method_', '')}</strong>`;
    return `<strong>${factor.feature}</strong> has a value of <strong>${val}</strong>`;
}

// ===== BUILD FACTOR CARDS =====
function buildFactorCards(explanation) {
    const container = document.getElementById('factor-list');
    container.innerHTML = '';

    const maxAbs = Math.max(...explanation.map(e => Math.abs(e.shap_value)), 0.01);

    // Show top 8 most impactful factors
    const topFactors = explanation.slice(0, 8);

    topFactors.forEach((exp, index) => {
        const isPositive = exp.shap_value > 0;
        const widthPct = Math.max((Math.abs(exp.shap_value) / maxAbs) * 100, 5);

        const item = document.createElement('div');
        item.className = 'factor-item';
        item.style.animationDelay = `${index * 0.05}s`;

        const cleanVal = exp.value
            .replace('type_', '')
            .replace('method_', '');

        // Strength label
        const absVal = Math.abs(exp.shap_value);
        let strengthLabel;
        if (absVal > 0.1) strengthLabel = 'Strong impact';
        else if (absVal > 0.03) strengthLabel = 'Moderate impact';
        else if (absVal > 0.01) strengthLabel = 'Small impact';
        else strengthLabel = 'Tiny impact';

        item.innerHTML = `
            <div class="factor-icon ${isPositive ? 'positive' : 'negative'}">
                ${getEmoji(exp.feature)}
            </div>
            <div class="factor-body">
                <div class="factor-name">${getCleanName(exp.feature)}</div>
                <div class="factor-value">Value: ${cleanVal} • ${strengthLabel}</div>
            </div>
            <div class="factor-impact">
                <span class="factor-tag ${isPositive ? 'helped' : 'hurt'}">
                    ${isPositive ? '▲ Helped' : '▼ Hurt'}
                </span>
                <div class="factor-bar-track">
                    <div class="factor-bar-fill ${isPositive ? 'positive' : 'negative'}" style="width: 0%"></div>
                </div>
            </div>
        `;

        container.appendChild(item);

        // Animate bar fill
        setTimeout(() => {
            item.querySelector('.factor-bar-fill').style.width = `${widthPct}%`;
        }, 200 + index * 80);
    });
}

// ===== BUILD SUGGESTIONS =====
function buildSuggestions(explanation, isHigh, inputData) {
    const container = document.getElementById('suggestions-list');
    container.innerHTML = '';

    const suggestions = [];

    // Find key factors
    const discountFactor = explanation.find(e => e.feature.toLowerCase().includes('discount'));
    const quantityFactor = explanation.find(e => e.feature.toLowerCase().includes('quantity'));
    const priceFactor = explanation.find(e => e.feature.toLowerCase().includes('unit price'));
    const shippingFactor = explanation.find(e => e.feature.toLowerCase().includes('shipping'));

    if (!isHigh) {
        // Suggestions to improve toward high sales
        if (discountFactor && discountFactor.shap_value < 0 && parseFloat(inputData.discount) > 10) {
            suggestions.push({
                icon: '🏷️',
                text: `Try <strong>reducing the discount</strong> from ${inputData.discount}% to below 10%. High discounts are significantly pulling the prediction toward Low Sales.`
            });
        }
        if (quantityFactor && parseFloat(inputData.quantity) < 50) {
            suggestions.push({
                icon: '📦',
                text: `<strong>Increase the quantity</strong> above 50 units. Quantity is usually the strongest factor for achieving High Sales predictions.`
            });
        }
        if (priceFactor && priceFactor.shap_value < 0) {
            suggestions.push({
                icon: '💰',
                text: `Consider <strong>adjusting the unit price</strong>. The current price of ₹${inputData.unit_price} is pulling toward Low Sales.`
            });
        }
        if (shippingFactor && shippingFactor.shap_value < 0 && parseFloat(inputData.shipping_cost) > 80) {
            suggestions.push({
                icon: '🚚',
                text: `<strong>Lower shipping costs</strong> if possible. At ₹${inputData.shipping_cost}, it's negatively affecting the prediction.`
            });
        }
        if (suggestions.length === 0) {
            suggestions.push({
                icon: '💡',
                text: `Try experimenting with <strong>higher quantities</strong> or <strong>lower discounts</strong> to see how the prediction changes.`
            });
        }
    } else {
        // Already high sales — what's helping
        suggestions.push({
            icon: '✅',
            text: `Great news! The current combination of inputs is working well. The transaction is predicted as High Sales.`
        });
        if (discountFactor && discountFactor.shap_value < -0.02) {
            suggestions.push({
                icon: '🏷️',
                text: `<strong>Pro tip:</strong> Even though the prediction is High Sales, reducing the ${inputData.discount}% discount could make the model even more confident.`
            });
        }
        if (quantityFactor && quantityFactor.shap_value > 0.05) {
            suggestions.push({
                icon: '📦',
                text: `The <strong>quantity of ${inputData.quantity} items</strong> is the key driver here. This is the biggest reason for the High Sales prediction.`
            });
        }
    }

    suggestions.forEach((s, i) => {
        const item = document.createElement('div');
        item.className = 'suggestion-item';
        item.style.animationDelay = `${i * 0.1}s`;
        item.innerHTML = `
            <span class="suggestion-icon">${s.icon}</span>
            <span>${s.text}</span>
        `;
        container.appendChild(item);
    });
}

// ===== BUILD SHAP CHART (Technical) =====
function buildShapChart(explanation) {
    const shapContainer = document.getElementById('shap-chart');
    shapContainer.innerHTML = '';

    const maxAbsShap = Math.max(...explanation.map(e => Math.abs(e.shap_value)), 0.01);

    explanation.forEach(exp => {
        const row = document.createElement('div');
        row.className = 'shap-row';

        const isPositive = exp.shap_value > 0;
        const widthPercent = (Math.abs(exp.shap_value) / maxAbsShap) * 50;

        let displayValue = exp.value ? `(${exp.value})` : '';
        let sign = exp.shap_value > 0 ? '+' : '';

        row.innerHTML = `
            <div class="shap-info">
                <span class="shap-feature">${exp.feature} ${displayValue}</span>
                <span class="shap-val-text" style="color: ${isPositive ? 'var(--success)' : 'var(--danger)'}">
                    ${sign}${exp.shap_value}
                </span>
            </div>
            <div class="bar-container">
                <div class="bar ${isPositive ? 'positive' : 'negative'}" style="width: ${widthPercent}%"></div>
            </div>
        `;
        shapContainer.appendChild(row);
    });
}
