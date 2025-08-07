# Centra SDK

The **Centra SDK** is a comprehensive FastAPI-based Software Development Kit designed to simplify the integration of third-party platforms with Guardicore's Centra platform. This SDK provides a standardized framework for building connectors that handle security policies, inventory management, operations monitoring, and more.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Core Components](#core-components)
- [Router Modules](#router-modules)
- [Handler Implementation](#handler-implementation)
- [Models and Data Types](#models-and-data-types)
- [Examples](#examples)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Contributing](#contributing)

## Overview

The Centra SDK serves as a bridge between external security platforms and Guardicore's centralized security management system. It provides:

- **Standardized API contracts** for consistent integration across different platforms
- **Handler registry system** for managing custom business logic
- **Comprehensive data models** generated from OpenAPI specifications
- **Built-in routing** for all major connector operations
- **Type safety** with Pydantic validation

## Features

### 🔧 **Modular Architecture**
- Clean separation between routing, business logic, and data models
- Pluggable handler system for custom implementations
- FastAPI-based REST API with automatic documentation

### 🛡️ **Security Operations**
- **Enforcement**: Policy management and rule enforcement
- **Inventory**: Asset discovery and management
- **Operations**: Health monitoring and configuration management
- **Logging**: Centralized logging and audit trails

### 📊 **Comprehensive Monitoring**
- Health checks and status reporting
- Metrics collection and reporting
- Configuration management
- Onboarding process management

### 🔄 **Platform Integration**
- Support for multiple cloud platforms (Azure, AWS, etc.)
- Agent management and control
- Network topology discovery
- Asset lookup and classification

## Installation

### Prerequisites
- Python 3.12 or higher
- Poetry (recommended) or pip

### Using Poetry (Recommended)
```bash
# Clone the repository
git clone https://github.com/guardicore/contracts.git
cd contracts/sdk

# Install dependencies
poetry install

# Activate the virtual environment
poetry shell
```

### Using pip
```bash
# Install from source
pip install -e .

# Or install dependencies directly
pip install fastapi uvicorn
```

## Quick Start

### 1. Create a Basic Connector

```python
from centra_sdk.main import app
from centra_sdk.routers.health import registry as health_registry, HealthHandler
from centra_sdk.models.connector.v1.operations.health import V1OperationsHealthGetResponse
import uvicorn

@health_registry.register()
class MyHealthHandler(HealthHandler):
    def get_integration_status(self) -> V1OperationsHealthGetResponse:
        return V1OperationsHealthGetResponse(
            overall_status="up",
            component_id="my-connector-id",
            component_type="custom_connector"
        )

# Run the server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 2. Start the Development Server

```bash
# Using uvicorn directly
uvicorn centra_sdk.main:app --reload --host 0.0.0.0 --port 8000

# Access the API documentation
# http://localhost:8000/docs
```

## Architecture

The Centra SDK follows a layered architecture pattern:

```
┌─────────────────────────────────────┐
│              FastAPI App            │
│              (main.py)              │
├─────────────────────────────────────┤
│               Routers               │
│  (health, inventory, enforcement,   │
│   operations, agents, etc.)         │
├─────────────────────────────────────┤
│           Handler Registry          │
│        (handler_registry.py)        │
├─────────────────────────────────────┤
│          Business Logic             │
│        (Custom Handlers)            │
├─────────────────────────────────────┤
│            Data Models              │
│         (Pydantic Models)           │
└─────────────────────────────────────┘
```

## Core Components

### 1. **Handler Registry** (`handler_registry.py`)

The `HandlerRegistry` class provides a decorator-based system for registering and managing custom business logic handlers:

```python
from centra_sdk.handler_registry import HandlerRegistry

# Create a registry for a specific domain
registry = HandlerRegistry(name="my_connector")

@registry.register(tag="production")
class MyHandler:
    def process_request(self, data):
        # Custom business logic here
        return {"status": "processed"}

# Call handler methods
result = registry.call_handler("process_request", data, tag="production")
```

**Key Features:**
- Decorator-based registration
- Tag-based handler organization
- Automatic error handling and HTTP response generation
- Logging and debugging support

### 2. **Main Application** (`main.py`)

The central FastAPI application that:
- Configures the API metadata and documentation
- Registers all router modules
- Provides the root endpoint
- Manages the application lifecycle

### 3. **Dependencies** (`dependencies.py`)

Central import module that provides access to all data models and types used throughout the SDK.

## Router Modules

The SDK includes several router modules, each handling specific aspects of connector functionality:

### 🏥 **Health Router** (`routers/health.py`)
Manages connector health and status reporting:

```python
@health_registry.register()
class MyHealthHandler(HealthHandler):
    def get_integration_flags(self) -> V1OperationsFlagsGetResponse:
        """Return integration capability flags"""
        pass
    
    def get_integration_status(self) -> V1OperationsHealthGetResponse:
        """Return current health status"""
        pass
    
    def get_integration_metrics(self) -> V1OperationsMetricsGetResponse:
        """Return performance metrics"""
        pass
```

### 📦 **Inventory Router** (`routers/inventory.py`)
Handles asset discovery and inventory management:

```python
@inventory_registry.register()
class MyInventoryHandler(InventoryHandler):
    def get_labels(self, cursor: int = 0, page_size: int = 100) -> Labels:
        """Retrieve asset labels"""
        pass
    
    def get_inventory(self, cursor: int = 0, page_size: int = 100) -> Inventory:
        """Retrieve asset inventory"""
        pass
    
    def post_assets(self, inventory_id: str, asset_type: str, body: Any):
        """Create or update assets"""
        pass
```

### 🛡️ **Enforcement Router** (`routers/enforcement.py`)
Manages security policy enforcement:

```python
@enforcement_registry.register()
class MyEnforcementHandler(EnforcementHandler):
    def set_enforcement_policy(self, body: EnforcementPolicy):
        """Apply security policies"""
        pass
    
    def get_enforcement_policy_inventory(self) -> EnforcementPolicyInventory:
        """Retrieve current policy inventory"""
        pass
```

### 🎛️ **Operations Router** (`routers/operations.py`)
Handles operational tasks like configuration and logging:

```python
@operations_registry.register()
class MyOperationsHandler(OperationsHandler):
    def get_config_options(self) -> InternalConfigMetadata:
        """Get available configuration options"""
        pass
    
    def set_config(self, body: InternalConfig):
        """Update connector configuration"""
        pass
```

### Other Routers:
- **Agents Router**: Agent management and control
- **Control Router**: Connector control operations
- **Info Router**: Integration information and metadata
- **Logging Router**: Log management and collection
- **Onboarding Router**: Platform onboarding processes

## Handler Implementation

### Creating Custom Handlers

1. **Inherit from Base Handler Classes**:
```python
from centra_sdk.routers.inventory import InventoryHandler, registry

@registry.register(tag="my_platform")
class MyPlatformInventoryHandler(InventoryHandler):
    def __init__(self):
        super().__init__()
        # Initialize your platform-specific clients
        self.platform_client = MyPlatformClient()
```

2. **Implement Required Methods**:
```python
def get_inventory(self, cursor: int = 0, page_size: int = 100) -> Inventory:
    # Fetch data from your platform
    assets = self.platform_client.get_assets(offset=cursor, limit=page_size)
    
    # Transform to Centra format
    inventory_items = []
    for asset in assets:
        item = InventoryItem(
            item_id=asset.id,
            external_id=asset.external_id,
            ip_addresses=asset.ips,
            # ... map other fields
        )
        inventory_items.append(item)
    
    return Inventory(
        inventory_items=inventory_items,
        total_count=len(inventory_items)
    )
```

3. **Handle Errors Gracefully**:
```python
def get_inventory(self, cursor: int = 0, page_size: int = 100) -> Inventory:
    try:
        # Your implementation
        pass
    except PlatformAPIException as e:
        # Log the error
        logger.error(f"Platform API error: {e}")
        # Let the registry handle HTTP error response
        raise HTTPException(status_code=503, detail=f"Platform unavailable: {e}")
```

## Models and Data Types

The SDK includes comprehensive data models generated from OpenAPI specifications. Key model categories include:

### **Common Models**
- `InventoryItem`: Represents discoverable assets
- `Label`: Key-value metadata for assets
- `NetworkTopology`: Network relationship data

### **Enforcement Models**
- `EnforcementPolicy`: Security policy definitions
- `PolicyRule`: Individual policy rules
- `Action`: Enforcement actions (allow, block, alert)

### **Operations Models**
- `ComponentHealth`: Health status information
- `InternalConfig`: Configuration data
- `LogStatus`: Logging status and metadata

### **Provider Models**
- `Inventory`: Asset inventory responses
- `NetworkTopology`: Network topology data
- `LookupRequest`: Asset lookup queries

## Examples

### Complete Inventory Handler Example

```python
from typing import Optional
from centra_sdk.routers.inventory import InventoryHandler, registry
from centra_sdk.models.connector.v1.provider.inventory import (
    Inventory, Labels, InventoryAssetType
)
from centra_sdk.models.connector.v1.common.inventory import (
    InventoryItem, Label, VMData, NetworkInterfaceData
)

@registry.register(tag="example_cloud")
class ExampleCloudInventoryHandler(InventoryHandler):
    def __init__(self):
        super().__init__()
        # Initialize your cloud provider client
        self.cloud_client = ExampleCloudClient()
    
    def get_labels(self, cursor: int = 0, page_size: int = 100) -> Labels:
        """Retrieve asset labels from the cloud provider"""
        labels_data = self.cloud_client.get_labels(offset=cursor, limit=page_size)
        
        labels = []
        for label_data in labels_data:
            label = Label(
                label_id=label_data['id'],
                key=label_data['key'],
                value=label_data['value'],
                labeled_items=label_data.get('tagged_resources', [])
            )
            labels.append(label)
        
        return Labels(labels=labels)
    
    def get_inventory(self, cursor: int = 0, page_size: int = 100) -> Inventory:
        """Retrieve VM inventory from the cloud provider"""
        vms_data = self.cloud_client.get_virtual_machines(
            offset=cursor, 
            limit=page_size
        )
        
        inventory_items = []
        for vm_data in vms_data:
            # Map network interfaces
            network_interfaces = []
            for nic in vm_data.get('network_interfaces', []):
                interface = NetworkInterfaceData(
                    name=nic['name'],
                    private_ip=nic.get('private_ip'),
                    public_ip=nic.get('public_ip'),
                    mac_address=nic.get('mac_address')
                )
                network_interfaces.append(interface)
            
            # Create VM data object
            vm_info = VMData(
                vm_name=vm_data['name'],
                vm_id=vm_data['id'],
                power_state=vm_data.get('power_state', 'unknown'),
                network_interfaces=network_interfaces,
                resource_group=vm_data.get('resource_group'),
                subscription_id=vm_data.get('subscription_id')
            )
            
            # Create inventory item
            item = InventoryItem(
                item_id=vm_data['id'],
                external_id=vm_data.get('external_id'),
                ip_addresses=vm_data.get('ip_addresses', []),
                vm_data=vm_info
            )
            inventory_items.append(item)
        
        return Inventory(
            inventory_items=inventory_items,
            total_count=len(inventory_items)
        )
```

### Health Check Handler Example

```python
from centra_sdk.routers.health import HealthHandler, registry
from centra_sdk.models.connector.v1.operations.health import (
    V1OperationsHealthGetResponse, V1OperationsFlagsGetResponse,
    ComponentDetails, Status
)

@registry.register(tag="example_connector")
class ExampleHealthHandler(HealthHandler):
    def __init__(self):
        super().__init__()
        self.component_id = "example-connector-v1.0"
        self.component_type = "example_cloud"
    
    def get_integration_flags(self) -> V1OperationsFlagsGetResponse:
        """Return connector capabilities"""
        return V1OperationsFlagsGetResponse(
            inventory_supported=True,
            enforcement_supported=True,
            logging_supported=False,
            agent_management_supported=False
        )
    
    def get_integration_status(self) -> V1OperationsHealthGetResponse:
        """Return current health status"""
        # Check various component health
        inventory_healthy = self._check_inventory_service()
        enforcement_healthy = self._check_enforcement_service()
        
        overall_status = "up" if inventory_healthy and enforcement_healthy else "degraded"
        
        return V1OperationsHealthGetResponse(
            component_id=self.component_id,
            component_type=self.component_type,
            component_details=ComponentDetails(
                dc_inventory_revision=12345,
                policy_revision=67890
            ),
            status=Status(overall_status=overall_status)
        )
    
    def _check_inventory_service(self) -> bool:
        """Check if inventory service is healthy"""
        try:
            # Perform health check logic
            return True
        except Exception:
            return False
    
    def _check_enforcement_service(self) -> bool:
        """Check if enforcement service is healthy"""
        try:
            # Perform health check logic
            return True
        except Exception:
            return False
```

## API Documentation

Once your application is running, you can access:

- **Interactive API Documentation**: `http://localhost:8000/docs`
- **Alternative Documentation**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

## Testing

The SDK includes comprehensive test suites demonstrating proper usage:

### Running Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/test_inventory_router.py
pytest tests/test_enforcement.py

# Run with coverage
pytest --cov=centra_sdk
```

### Test Examples

The test files provide excellent examples of how to implement handlers:

- `tests/test_inventory_router.py`: Complete inventory handler implementation
- `tests/test_enforcement.py`: Enforcement policy handling examples
- `tests/gc_*.py`: Real-world integration examples

## Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** and add tests
4. **Ensure tests pass**: `pytest`
5. **Commit your changes**: `git commit -m 'Add amazing feature'`
6. **Push to the branch**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

### Development Guidelines

- Follow PEP 8 style guidelines
- Add comprehensive docstrings
- Include unit tests for new functionality
- Update documentation as needed
- Ensure backward compatibility

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions, issues, or contributions:

- **GitHub Issues**: [https://github.com/guardicore/contracts/issues](https://github.com/guardicore/contracts/issues)
- **Documentation**: [https://github.com/guardicore/contracts](https://github.com/guardicore/contracts)
- **Email**: ivasylen@akamai.com

---

**Built with ❤️ by the Guardicore Team**
