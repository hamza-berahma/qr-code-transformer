function toggleInputType() {
    const inputType = document.getElementById('input-type').value;
    const messagesInput = document.getElementById('messages-input');
    const imageInput = document.getElementById('image-input');
    
    if (inputType === 'messages') {
        messagesInput.style.display = 'contents';
        imageInput.style.display = 'none';
    } else {
        messagesInput.style.display = 'none';
        imageInput.style.display = 'contents';
    }
}

async function transformQR() {
    const inputType = document.getElementById('input-type').value;
    const resultsSection = document.getElementById('results-section');
    const loading = document.getElementById('loading');
    const errorDiv = document.getElementById('error');
    
    // Hide previous results and errors
    resultsSection.style.display = 'none';
    errorDiv.style.display = 'none';
    loading.style.display = 'block';
    
    try {
        const formData = new FormData();
        const useExact = document.getElementById('use-exact').checked;
        const respectEcc = document.getElementById('respect-ecc').checked;
        
        // ECC level is now automatically optimized - no need to send it
        formData.append('use_exact', useExact);
        formData.append('respect_ecc', respectEcc);
        
        if (inputType === 'messages') {
            const messageA = document.getElementById('message-a').value;
            const messageB = document.getElementById('message-b').value;
            
            if (!messageB) {
                throw new Error('Target message (B) is required');
            }
            
            if (!messageA) {
                throw new Error('Original message (A) is required for message-based transformation');
            }
            
            formData.append('message_a', messageA);
            formData.append('message_b', messageB);
        } else {
            const fileInput = document.getElementById('qr-file');
            const messageB = document.getElementById('message-b-image').value;
            
            if (!fileInput.files || fileInput.files.length === 0) {
                throw new Error('Please select a QR code image');
            }
            
            if (!messageB) {
                throw new Error('Target message is required');
            }
            
            formData.append('file', fileInput.files[0]);
            formData.append('message_b', messageB);
        }
        
        const response = await fetch('/api/transform', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Transformation failed');
        }
        
        const result = await response.json();
        
        // Display results
        displayResults(result);
        
    } catch (error) {
        errorDiv.textContent = `Error: ${error.message}`;
        errorDiv.style.display = 'block';
    } finally {
        loading.style.display = 'none';
    }
}

function displayResults(result) {
    const resultsSection = document.getElementById('results-section');
    if (!resultsSection) {
        console.error('Results section not found');
        return;
    }
    
    // Update stats with null checks
    const minFlipsEl = document.getElementById('min-flips');
    const withinEccEl = document.getElementById('within-ecc');
    const changePctEl = document.getElementById('change-pct');
    
    if (minFlipsEl) {
        minFlipsEl.textContent = result.min_flips || 0;
    } else {
        console.warn('min-flips element not found');
    }
    
    if (withinEccEl) {
        withinEccEl.textContent = result.within_ecc ? 'Yes' : 'No';
    } else {
        console.warn('within-ecc element not found');
    }
    
    if (changePctEl && result.stats && result.stats.change_percentage !== undefined) {
        changePctEl.textContent = result.stats.change_percentage.toFixed(2) + '%';
    } else if (!changePctEl) {
        console.warn('change-pct element not found');
    }
    
    // Display algorithm name and ECC level
    const algorithmNameEl = document.getElementById('algorithm-name');
    if (algorithmNameEl && result.algorithm) {
        // Extract algorithm and ECC level from format like "qart-h" or "ilp-m"
        const parts = result.algorithm.split('-');
        const algo = parts[0];
        const ecc = parts.length > 1 ? parts[1].toUpperCase() : '';
        
        const algorithmNames = {
            'qart': 'QArt (RS Linearity)',
            'ilp': 'ILP (Integer Linear Programming)',
            'hybrid': 'Hybrid (Control Model)',
            'unknown': 'Unknown'
        };
        
        const algoName = algorithmNames[algo] || algo.toUpperCase();
        const eccInfo = ecc ? ` - ECC ${ecc}` : '';
        algorithmNameEl.textContent = algoName + eccInfo;
    }
    
    // Display algorithm comparison if available
    if (result.algorithm_results) {
        displayAlgorithmComparison(result.algorithm_results, result.algorithm);
    }
    
    // Display individual QR code images in table
    if (result.images) {
        const originalImg = document.getElementById('original-image');
        const targetImg = document.getElementById('target-image');
        const transformedImg = document.getElementById('transformed-image');
        const changesImg = document.getElementById('changes-image');
        
        if (originalImg && result.images.original) {
            originalImg.src = 'data:image/png;base64,' + result.images.original;
        } else if (!originalImg) {
            console.error('original-image element not found');
        }
        
        if (targetImg && result.images.target) {
            targetImg.src = 'data:image/png;base64,' + result.images.target;
        } else if (!targetImg) {
            console.error('target-image element not found');
        }
        
        if (transformedImg && result.images.transformed) {
            transformedImg.src = 'data:image/png;base64,' + result.images.transformed;
        } else if (!transformedImg) {
            console.error('transformed-image element not found');
        }
        
        if (changesImg && result.images.changes) {
            changesImg.src = 'data:image/png;base64,' + result.images.changes;
        } else if (!changesImg) {
            console.error('changes-image element not found');
        }
    } else if (result.comparison_image) {
        // Fallback for old format
        const comparisonImg = document.getElementById('comparison-image');
        if (comparisonImg) {
            comparisonImg.src = 'data:image/png;base64,' + result.comparison_image;
        }
    } else {
        console.warn('No images found in result');
    }
    
    // Display insights
    const insightsContent = document.getElementById('insights-content');
    if (insightsContent && result.insights) {
        insightsContent.innerHTML = generateInsightsHTML(result.insights);
    } else if (!insightsContent) {
        console.warn('insights-content element not found');
    }
    
    // Smooth scroll to results
    resultsSection.style.display = 'block';
    setTimeout(() => {
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
    
    // Animate stat cards
    const statCards = document.querySelectorAll('.stat-card');
    statCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        setTimeout(() => {
            card.style.transition = 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 100 + (index * 100));
    });
    
    // Animate QR cards
    const qrCards = document.querySelectorAll('.qr-card');
    qrCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        setTimeout(() => {
            card.style.transition = 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 300 + (index * 100));
    });
}

function generateInsightsHTML(insights) {
    let html = '<div class="insights-detail">';
    
    html += '<h4>Transformation Summary</h4>';
    html += `<p>Module squares to change: ${insights.transformation_summary.min_flips}</p>`;
    html += `<p>Within ECC capacity: ${insights.transformation_summary.within_ecc ? 'Yes' : 'No'}</p>`;
    
    html += '<h4>ECC Information</h4>';
    html += `<p>Level: ${insights.ecc_info.level}</p>`;
    html += `<p>Capacity: ${insights.ecc_info.capacity} codewords</p>`;
    html += `<p>Utilization: ${insights.ecc_info.utilization.toFixed(1)}%</p>`;
    
    html += '<h4>Matrix Information</h4>';
    html += `<p>Size: ${insights.matrix_info.size}</p>`;
    html += `<p>Total modules: ${insights.matrix_info.total_modules}</p>`;
    html += `<p>Change percentage: ${insights.matrix_info.change_percentage.toFixed(2)}%</p>`;
    
    html += '<h4>Messages</h4>';
    html += `<p>Original: "${insights.messages.original}"</p>`;
    html += `<p>Target: "${insights.messages.target}"</p>`;
    
    if (insights.recommendations && insights.recommendations.length > 0) {
        html += '<h4>Recommendations</h4>';
        insights.recommendations.forEach(rec => {
            html += `<div class="recommendation">${rec}</div>`;
        });
    }
    
    html += '</div>';
    return html;
}

function displayAlgorithmComparison(algorithmResults, bestAlgorithm) {
    const comparisonDiv = document.getElementById('algorithm-comparison');
    const comparisonContent = document.getElementById('algorithm-comparison-content');
    
    if (!comparisonDiv || !comparisonContent || !algorithmResults) {
        return;
    }
    
    // Only show if we have multiple algorithms
    const algorithmCount = Object.keys(algorithmResults).filter(
        key => !algorithmResults[key].error
    ).length;
    
    if (algorithmCount <= 1) {
        comparisonDiv.style.display = 'none';
        return;
    }
    
    let html = '<div class="algorithm-grid">';
    
    for (const [algoName, algoData] of Object.entries(algorithmResults)) {
        if (algoData.error) {
            continue;
        }
        
        const isBest = algoName === bestAlgorithm;
        
        // Extract algorithm and ECC level
        const parts = algoName.split('-');
        const algo = parts[0];
        const ecc = parts.length > 1 ? parts[1].toUpperCase() : algoData.ecc_level || '?';
        
        const algorithmNames = {
            'qart': 'QArt (RS Linearity)',
            'ilp': 'ILP (Integer Linear Programming)',
            'hybrid': 'Hybrid (Control Model)'
        };
        
        html += `<div class="algorithm-card ${isBest ? 'algorithm-best' : ''}">`;
        html += `<div class="algorithm-header">`;
        html += `<span class="algorithm-name">${algorithmNames[algo] || algo.toUpperCase()} - ECC ${ecc}</span>`;
        if (isBest) {
            html += `<span class="algorithm-badge">Best</span>`;
        }
        html += `</div>`;
        html += `<div class="algorithm-stats">`;
        html += `<div class="algorithm-stat"><span class="stat-label">Flips:</span> <span class="stat-value">${algoData.min_flips || 'N/A'}</span></div>`;
        html += `<div class="algorithm-stat"><span class="stat-label">ECC Level:</span> <span class="stat-value">${ecc}</span></div>`;
        html += `<div class="algorithm-stat"><span class="stat-label">Success:</span> <span class="stat-value">${algoData.success ? 'Yes' : 'No'}</span></div>`;
        html += `<div class="algorithm-stat"><span class="stat-label">Within ECC:</span> <span class="stat-value">${algoData.within_ecc ? 'Yes' : 'No'}</span></div>`;
        if (algoData.padding_flips !== undefined && algoData.error_injection_flips !== undefined) {
            html += `<div class="algorithm-stat"><span class="stat-label">Padding Flips:</span> <span class="stat-value">${algoData.padding_flips}</span></div>`;
            html += `<div class="algorithm-stat"><span class="stat-label">Error Injection:</span> <span class="stat-value">${algoData.error_injection_flips}</span></div>`;
        }
        if (algoData.solver_time !== undefined) {
            html += `<div class="algorithm-stat"><span class="stat-label">Time:</span> <span class="stat-value">${algoData.solver_time.toFixed(3)}s</span></div>`;
        }
        html += `</div>`;
        html += `</div>`;
    }
    
    html += '</div>';
    comparisonContent.innerHTML = html;
    comparisonDiv.style.display = 'block';
}

