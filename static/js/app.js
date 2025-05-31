let statusInterval;

async function fetchVMStatus() {
    try {
        const response = await fetch('/api/vm/status');
        const data = await response.json();
        
        if (data.status === 'success') {
            updateVMStatus(data);
        } else {
            showMessage('Error fetching VM status', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showMessage('Failed to connect to server', 'error');
    }
}

async function fetchVMUsage() {
    try {
        const response = await fetch('/api/vm/usage');
        const data = await response.json();
        
        if (data.status === 'success') {
            updateUsageDisplay(data);
        } else {
            showMessage('Error fetching usage data', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showMessage('Failed to fetch usage data', 'error');
    }
}

function updateVMStatus(data) {
    document.getElementById('vm-name').textContent = data.vmName;
    
    const powerStateElement = document.getElementById('power-state');
    const powerState = data.powerState.toLowerCase();
    powerStateElement.textContent = data.powerState;
    
    // Remove all state classes
    powerStateElement.classList.remove('running', 'stopped', 'deallocated', 'starting', 'stopping');
    
    // Add appropriate class based on state
    if (powerState === 'running') {
        powerStateElement.classList.add('running');
        document.getElementById('start-btn').disabled = true;
        document.getElementById('stop-btn').disabled = false;
    } else if (powerState === 'stopped' || powerState === 'deallocated') {
        powerStateElement.classList.add(powerState);
        document.getElementById('start-btn').disabled = false;
        document.getElementById('stop-btn').disabled = true;
    } else if (powerState === 'starting' || powerState === 'stopping') {
        powerStateElement.classList.add(powerState);
        document.getElementById('start-btn').disabled = true;
        document.getElementById('stop-btn').disabled = true;
    }
}

function updateUsageDisplay(data) {
    document.getElementById('usage-month').textContent = data.month;
    
    // Check if usage data is available (0 means unknown)
    if (data.runningHours === 0) {
        document.getElementById('running-hours').textContent = 'Unknown';
        document.getElementById('estimated-cost').textContent = 'Unknown';
    } else {
        document.getElementById('running-hours').textContent = data.runningHours + ' hours';
        document.getElementById('estimated-cost').textContent = '€' + data.estimatedCost.toFixed(2);
    }
    
    document.getElementById('hourly-cost').textContent = '€' + data.hourlyCost.toFixed(2);
}

async function startVM() {
    if (!confirm('Are you sure you want to start the VM?')) {
        return;
    }
    
    showMessage('Starting VM...', 'info');
    document.getElementById('start-btn').disabled = true;
    
    try {
        const response = await fetch('/api/vm/start', { method: 'POST' });
        const data = await response.json();
        
        if (data.status === 'success') {
            showMessage('VM start initiated successfully', 'success');
            setTimeout(() => {
                fetchVMStatus();
                hideMessage();
            }, 3000);
        } else {
            showMessage('Error starting VM: ' + data.message, 'error');
            document.getElementById('start-btn').disabled = false;
        }
    } catch (error) {
        console.error('Error:', error);
        showMessage('Failed to start VM', 'error');
        document.getElementById('start-btn').disabled = false;
    }
}

async function stopVM() {
    if (!confirm('Are you sure you want to stop the VM? This will deallocate it to avoid charges.')) {
        return;
    }
    
    showMessage('Stopping VM...', 'info');
    document.getElementById('stop-btn').disabled = true;
    
    try {
        const response = await fetch('/api/vm/stop', { method: 'POST' });
        const data = await response.json();
        
        if (data.status === 'success') {
            showMessage('VM stop initiated successfully', 'success');
            setTimeout(() => {
                fetchVMStatus();
                hideMessage();
            }, 3000);
        } else {
            showMessage('Error stopping VM: ' + data.message, 'error');
            document.getElementById('stop-btn').disabled = false;
        }
    } catch (error) {
        console.error('Error:', error);
        showMessage('Failed to stop VM', 'error');
        document.getElementById('stop-btn').disabled = false;
    }
}

function showMessage(text, type) {
    const messageElement = document.getElementById('message');
    messageElement.textContent = text;
    messageElement.className = 'message ' + type;
}

function hideMessage() {
    const messageElement = document.getElementById('message');
    messageElement.className = 'message';
}

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    // Initial fetch
    fetchVMStatus();
    fetchVMUsage();
    
    // Set up auto-refresh every 30 seconds
    statusInterval = setInterval(() => {
        fetchVMStatus();
        fetchVMUsage();
    }, 30000);
});

// Clean up interval on page unload
window.addEventListener('beforeunload', () => {
    if (statusInterval) {
        clearInterval(statusInterval);
    }
});