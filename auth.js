// REPLACE the analyze button click handler in app.html with this:

analyzeBtn.addEventListener('click', async function() {
    const contractTextArea = document.getElementById('contractText');
    const otherParty = document.getElementById('otherParty');
    const selectedRadio = document.querySelector('input[name="analysis"]:checked');
    const otherInput = document.getElementById('otherInput');
    
    // Validation
    if (!contractTextArea || !contractTextArea.value.trim()) {
        alert('Please enter or upload contract text to analyze');
        if (contractTextArea) contractTextArea.focus();
        return;
    }
    
    if (contractTextArea.value.trim().length < 50) {
        alert('Please enter at least 50 characters of contract text');
        return;
    }
    
    if (!selectedRadio) {
        alert('Please select an analysis type');
        return;
    }
    
    const selectedAnalysis = selectedRadio.value;
    const additionalInstructions = selectedAnalysis === 'Others' && otherInput ? otherInput.value.trim() : '';
    
    if (selectedAnalysis === 'Others' && !additionalInstructions) {
        alert('Please specify what analysis you need in "Additional instructions"');
        if (otherInput) otherInput.focus();
        return;
    }
    
    // Get user data
    const userData = JSON.parse(localStorage.getItem('contractGuardUser') || '{}');
    
    // Show loading
    analyzeBtn.innerHTML = '<i class="fa fa-spinner fa-spin"></i> Analyzing with AI...';
    analyzeBtn.disabled = true;
    
    try {
        // Prepare request data for REAL Gemini API
        const requestData = {
            contract_text: contractTextArea.value.trim(),
            analysis_type: selectedAnalysis,
            additional_instructions: additionalInstructions,
            user_data: userData,
            other_party: otherParty ? otherParty.value.trim() : ''
        };
        
        console.log('Sending to Gemini API:', requestData);
        
        // Call REAL backend API
        const response = await fetch('http://localhost:5000/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        });
        
        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }
        
        const result = await response.json();
        
        // Display REAL Gemini analysis
        if (outputBox) {
            if (result.error) {
                outputBox.innerHTML = `
                    <div style="color: #ff6b6b;">
                        <h3><i class="fa fa-exclamation-triangle"></i> API Error</h3>
                        <p>${result.error}</p>
                        <p>${result.message || ''}</p>
                    </div>
                `;
            } else {
                // Format the Gemini response
                const formattedText = result.analysis.replace(/\n/g, '<br>')
                    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                    .replace(/\* /g, '• ');
                
                outputBox.innerHTML = `
                    <div style="color: #a5b4cb;">
                        <h3 style="color: #4cc9f0;"><i class="fa fa-file-contract"></i> AI Analysis Results</h3>
                        <div style="background: rgba(76, 201, 240, 0.1); padding: 15px; border-radius: 10px; margin: 15px 0;">
                            <p><strong><i class="fa fa-tag"></i> Analysis Type:</strong> ${result.analysis_type || selectedAnalysis}</p>
                            <p><strong><i class="fa fa-clock"></i> Generated at:</strong> ${new Date().toLocaleString()}</p>
                            <p><strong><i class="fa fa-robot"></i> AI Model:</strong> ${result.model_used || 'Gemini AI'}</p>
                        </div>
                        <hr style="border-color: rgba(255,255,255,0.1); margin: 20px 0;">
                        <div style="line-height: 1.6; font-size: 1.1rem; color: #ffffff;">
                            ${formattedText}
                        </div>
                        <div style="margin-top: 25px; padding: 15px; background: rgba(114, 239, 221, 0.1); border-radius: 10px;">
                            <p><strong><i class="fa fa-lightbulb"></i> Note:</strong> This AI-generated analysis by Gemini. For legally binding contracts, consult with a legal professional.</p>
                        </div>
                    </div>
                `;
            }
            
            outputBox.classList.add('show');
            outputBox.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
        
    } catch (error) {
        console.error('Analysis error:', error);
        
        // Show error
        if (outputBox) {
            outputBox.innerHTML = `
                <div style="color: #ff6b6b; padding: 20px;">
                    <h3><i class="fa fa-exclamation-triangle"></i> Connection Error</h3>
                    <p><strong>Error:</strong> ${error.message}</p>
                    <p><strong>Solution:</strong> Please make sure:</p>
                    <ol style="margin-left: 20px; margin-top: 10px;">
                        <li>The Python backend is running (python app.py)</li>
                        <li>Server is accessible at http://localhost:5000</li>
                        <li>Your internet connection is working</li>
                        <li>Gemini API key is correctly configured</li>
                    </ol>
                    <p style="margin-top: 15px;">Trying fallback analysis...</p>
                </div>
            `;
            outputBox.classList.add('show');
            
            // Fallback to simulated analysis after 2 seconds
            setTimeout(() => {
                const fallbackAnalysis = generateFallbackAnalysis(
                    contractTextArea.value.trim(),
                    selectedAnalysis,
                    additionalInstructions
                );
                outputBox.innerHTML = fallbackAnalysis;
            }, 2000);
        }
        
    } finally {
        // Reset button
        analyzeBtn.innerHTML = 'Analyze Contract <i class="fa fa-magnifying-glass"></i>';
        analyzeBtn.disabled = false;
    }
});