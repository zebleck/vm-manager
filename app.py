from flask import Flask, render_template, jsonify
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from datetime import datetime, timezone
import os
import logging
from vm_monitor import VMMonitor
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Azure configuration from environment variables
SUBSCRIPTION_ID = os.environ.get('AZURE_SUBSCRIPTION_ID')
RESOURCE_GROUP = os.environ.get('AZURE_RESOURCE_GROUP')
VM_NAME = os.environ.get('AZURE_VM_NAME')
VM_HOURLY_COST = float(os.environ.get('VM_HOURLY_COST_EUR', '0.53'))

# Initialize Azure clients
credential = DefaultAzureCredential()
compute_client = ComputeManagementClient(credential, SUBSCRIPTION_ID)
vm_monitor = VMMonitor()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/vm/status')
def get_vm_status():
    try:
        vm = compute_client.virtual_machines.instance_view(RESOURCE_GROUP, VM_NAME)
        
        # Get power state from instance view
        power_state = 'Unknown'
        for status in vm.statuses:
            if status.code.startswith('PowerState/'):
                power_state = status.code.split('/')[-1]
                break
        
        return jsonify({
            'status': 'success',
            'powerState': power_state,
            'vmName': VM_NAME
        })
    except Exception as e:
        logging.error(f"Error getting VM status: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/vm/start', methods=['POST'])
def start_vm():
    try:
        compute_client.virtual_machines.begin_start(RESOURCE_GROUP, VM_NAME).wait()
        return jsonify({'status': 'success', 'message': 'VM start initiated'})
    except Exception as e:
        logging.error(f"Error starting VM: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/vm/stop', methods=['POST'])
def stop_vm():
    try:
        # Deallocate to avoid charges
        compute_client.virtual_machines.begin_deallocate(RESOURCE_GROUP, VM_NAME).wait()
        return jsonify({'status': 'success', 'message': 'VM stop initiated'})
    except Exception as e:
        logging.error(f"Error stopping VM: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/vm/usage')
def get_vm_usage():
    try:
        # Get actual runtime from Azure Monitor
        running_hours = vm_monitor.get_monthly_runtime()
        now = datetime.now(timezone.utc)
        if running_hours is None:
            return jsonify({
                'status': 'success',
                'month': now.strftime('%B %Y'),
                'runningHours': 'unknown',
                'estimatedCost': 'unknown',
                'hourlyCost': VM_HOURLY_COST
            })
        # Calculate cost
        estimated_cost = running_hours * VM_HOURLY_COST
        return jsonify({
            'status': 'success',
            'month': now.strftime('%B %Y'),
            'runningHours': round(running_hours, 2),
            'estimatedCost': round(estimated_cost, 2),
            'hourlyCost': VM_HOURLY_COST
        })
    except Exception as e:
        logging.error(f"Error getting VM usage: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False)