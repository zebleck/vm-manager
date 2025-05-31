# VM Control Dashboard

A lightweight Azure web application for monitoring and managing Virtual Machine power states with cost tracking.

## Features

- View current VM power state (Running, Stopped, Deallocated)
- Start/Stop VM with one click
- Track monthly runtime hours
- Calculate estimated monthly costs
- Auto-refresh status every 30 seconds

## Prerequisites

- Azure subscription
- Azure VM to manage
- Azure App Service (B1 plan or higher)
- Managed Identity enabled on App Service

## Configuration

Set these environment variables in Azure App Service:

- `AZURE_SUBSCRIPTION_ID`: Your Azure Subscription ID
- `AZURE_RESOURCE_GROUP`: Resource Group containing the VM
- `AZURE_VM_NAME`: Name of the VM to monitor
- `VM_HOURLY_COST_EUR`: Hourly cost of your VM (e.g., 0.53)

## Deployment

1. Enable Managed Identity on your App Service
2. Grant the Managed Identity these roles on your VM:
   - Virtual Machine Contributor
   - Reader
3. Deploy code to App Service using Git or ZIP deployment
4. Set environment variables in App Service Configuration

## Security

- Uses Azure Managed Identity (no credentials in code)
- All VM operations require proper Azure RBAC permissions
- Consider adding Azure AD authentication for user access control

## Architecture

- **Backend**: Python Flask
- **Frontend**: Vanilla JavaScript with responsive design
- **Azure SDK**: azure-identity, azure-mgmt-compute
- **Hosting**: Azure App Service with Gunicorn