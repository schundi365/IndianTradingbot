/**
 * Strategy Recommendations Module - Simplified Version
 */

console.log('=== STRATEGY RECOMMENDATIONS SCRIPT LOADED ===');

// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('=== DOM READY - INITIALIZING STRATEGY RECOMMENDATIONS ===');
    
    // Find strategy selector
    const strategySelect = document.getElementById('config-strategy');
    console.log('Strategy selector found:', strategySelect !== null);
    
    if (!strategySelect) {
        console.error('Strategy selector not found!');
        return;
    }
    
    // Create recommendations container
    const recommendationsDiv = document.createElement('div');
    recommendationsDiv.id = 'strategy-recommendations';
    recommendationsDiv.style.cssText = 'margin: 1rem 0; padding: 1rem; background: #2B2F36; border: 2px solid #FCD535; border-radius: 8px; display: none;';
    
    // Insert after strategy selector
    const strategyGroup = strategySelect.closest('.form-group');
    if (strategyGroup) {
        strategyGroup.parentNode.insertBefore(recommendationsDiv, strategyGroup.nextSibling);
        console.log('=== RECOMMENDATIONS CONTAINER CREATED ===');
    } else {
        console.error('Could not find strategy form group');
        return;
    }
    
    // Add change listener
    strategySelect.addEventListener('change', function(e) {
        const strategy = e.target.value;
        console.log('=== STRATEGY CHANGED TO:', strategy, '===');
        
        if (!strategy || strategy === '') {
            recommendationsDiv.style.display = 'none';
            return;
        }
        
        // Show simple recommendations
        recommendationsDiv.innerHTML = `
            <div style="color: white;">
                <h4 style="color: #FCD535; margin: 0 0 1rem 0;">💡 ${strategy.toUpperCase()} Strategy Recommendations</h4>
                <p style="margin: 0.5rem 0;">This is a test to verify the recommendations panel is working.</p>
                <p style="margin: 0.5rem 0;">Strategy selected: <strong style="color: #FCD535;">${strategy}</strong></p>
                <button type="button" onclick="this.parentElement.parentElement.style.display='none'" 
                        style="margin-top: 1rem; padding: 0.5rem 1rem; background: #FCD535; color: #000; border: none; border-radius: 4px; cursor: pointer;">
                    Close
                </button>
            </div>
        `;
        recommendationsDiv.style.display = 'block';
        console.log('=== RECOMMENDATIONS PANEL DISPLAYED ===');
    });
    
    console.log('=== STRATEGY RECOMMENDATIONS INITIALIZED SUCCESSFULLY ===');
});
