from azure.monitor.query import MetricsQueryClient
from azure.identity import DefaultAzureCredential
from azure.mgmt.monitor import MonitorManagementClient
from azure.mgmt.compute import ComputeManagementClient
from datetime import datetime, timezone, timedelta
import os
import logging

class VMMonitor:
    def __init__(self):
        self.credential = DefaultAzureCredential()
        self.metrics_client = MetricsQueryClient(self.credential)
        self.monitor_client = MonitorManagementClient(self.credential, os.environ.get('AZURE_SUBSCRIPTION_ID'))
        self.compute_client = ComputeManagementClient(self.credential, os.environ.get('AZURE_SUBSCRIPTION_ID'))
        
        self.subscription_id = os.environ.get('AZURE_SUBSCRIPTION_ID')
        self.resource_group = os.environ.get('AZURE_RESOURCE_GROUP')
        self.vm_name = os.environ.get('AZURE_VM_NAME')
        
        # Construct resource ID for the VM
        self.vm_resource_id = (
            f"/subscriptions/{self.subscription_id}"
            f"/resourceGroups/{self.resource_group}"
            f"/providers/Microsoft.Compute/virtualMachines/{self.vm_name}"
        )
    
    def get_vm_power_state(self):
        """
        Get the current power state of the VM
        Returns: 'running', 'deallocated', 'stopped', or 'unknown'
        """
        try:
            # Get VM instance view to check power state
            vm = self.compute_client.virtual_machines.instance_view(
                resource_group_name=self.resource_group,
                vm_name=self.vm_name
            )
            
            # Check statuses for power state
            if vm.statuses:
                for status in vm.statuses:
                    if status.code:
                        if status.code.startswith('PowerState/'):
                            power_state = status.code.split('/')[-1]
                            return power_state.lower()
            
            return 'unknown'
            
        except Exception as e:
            logging.error(f"Error getting VM power state: {str(e)}")
            return 'unknown'
    
    def get_monthly_runtime(self):
        """
        Get the total runtime hours for the current month using VM availability metric
        """
        try:
            now = datetime.now(timezone.utc)
            start_of_month = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
            
            # Query VM availability metric which shows percentage of time VM was available
            response = self.metrics_client.query_resource(
                resource_uri=self.vm_resource_id,
                metric_names=["VmAvailabilityMetric"],
                timespan=(start_of_month, now),
                granularity=timedelta(hours=1),
                aggregations=["Average"]
            )
            
            running_hours = 0
            
            # Process the metric data
            if response.metrics:
                for metric in response.metrics:
                    if metric.name == "VmAvailabilityMetric" and metric.timeseries:
                        for timeseries in metric.timeseries:
                            for data_point in timeseries.data:
                                # VM Availability of 1 means running, 0 means not running
                                if data_point.average and data_point.average > 0:
                                    running_hours += data_point.average
            
            # Log current VM state for debugging
            current_state = self.get_vm_power_state()
            logging.info(f"Current VM state: {current_state}, Monthly runtime: {running_hours:.2f} hours")
            
            # If no data was found, treat as unknown
            if running_hours == 0:
                return None
            return running_hours
            
        except Exception as e:
            logging.error(f"Error querying VM metrics: {str(e)}")
            # Return None to indicate unknown/unavailable
            return None
    
    def get_detailed_runtime_info(self):
        """
        Get detailed runtime information including current state, monthly hours, and recent activity
        """
        try:
            # Get current state
            current_state = self.get_vm_power_state()
            
            # Get monthly runtime
            monthly_hours = self.get_monthly_runtime()
            
            # Get last few activity log entries for context
            now = datetime.now(timezone.utc)
            
            return {
                'current_state': current_state,
                'is_running': current_state == 'running',
                'monthly_runtime_hours': round(monthly_hours, 2),
                'monthly_runtime_days': round(monthly_hours / 24, 2),
                'timestamp': now.isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error getting detailed runtime info: {str(e)}")
            return {
                'error': str(e),
                'current_state': 'unknown',
                'is_running': False,
                'monthly_runtime_hours': 0,
                'monthly_runtime_days': 0,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }