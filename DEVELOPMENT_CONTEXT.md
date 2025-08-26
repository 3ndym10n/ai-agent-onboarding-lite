# 🛠️ VectorFlow Development Context

**Coding Patterns, Architectural Guidelines, and Development Standards**

## 🎯 **DEVELOPMENT PHILOSOPHY**

### **Hybrid Quant-Manual Approach**
- **Preserve human decision-making** - Never suggest full automation
- **Quantify instinctive patterns** - Add statistical validation
- **Maintain performance standards** - <100ms latency, 80-90% accuracy
- **Build on existing architecture** - Extend rather than replace

### **Code Quality Standards**
- **Async-first design** - Use async/await for all I/O operations
- **Type hints** - Full type annotation for all functions
- **Error handling** - Comprehensive exception handling with logging
- **Documentation** - Clear docstrings and inline comments

## 🏗️ **ARCHITECTURAL PATTERNS**

### **Service Layer Pattern**
```python
class BaseService:
    """Base class for all VectorFlow services"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.db_pool = None
        self.redis_client = None
    
    async def initialize(self):
        """Initialize service dependencies"""
        self.db_pool = await get_db_pool()
        self.redis_client = await get_redis_client()
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.db_pool:
            await self.db_pool.close()
        if self.redis_client:
            await self.redis_client.close()
```

### **Event-Driven Architecture**
```python
class EventBus:
    """Central event bus for inter-service communication"""
    
    def __init__(self):
        self.subscribers = defaultdict(list)
        self.logger = logging.getLogger(__name__)
    
    async def publish(self, event_type: str, event_data: Dict):
        """Publish event to all subscribers"""
        for handler in self.subscribers[event_type]:
            try:
                await handler(event_data)
            except Exception as e:
                self.logger.error(f"Event handler failed: {e}")
    
    def subscribe(self, event_type: str, handler: Callable):
        """Subscribe to event type"""
        self.subscribers[event_type].append(handler)
```

### **Repository Pattern**
```python
class MarketDataRepository:
    """Repository for market data operations"""
    
    def __init__(self, db_pool):
        self.db_pool = db_pool
    
    async def insert_market_event(self, event: Dict) -> int:
        """Insert market event and return ID"""
        async with self.db_pool.acquire() as conn:
            query = """
                INSERT INTO market_events (timestamp, symbol, event_type, data)
                VALUES ($1, $2, $3, $4)
                RETURNING id
            """
            result = await conn.fetchval(
                query,
                event['timestamp'],
                event['symbol'],
                event['type'],
                json.dumps(event['data'])
            )
            return result
    
    async def get_recent_events(self, symbol: str, limit: int = 100) -> List[Dict]:
        """Get recent market events for symbol"""
        async with self.db_pool.acquire() as conn:
            query = """
                SELECT * FROM market_events 
                WHERE symbol = $1 
                ORDER BY timestamp DESC 
                LIMIT $2
            """
            rows = await conn.fetch(query, symbol, limit)
            return [dict(row) for row in rows]
```

## 🔧 **CODING PATTERNS**

### **Async Context Managers**
```python
class AsyncResourceManager:
    """Manage async resources with context manager"""
    
    def __init__(self, resource_config: Dict):
        self.config = resource_config
        self.resource = None
    
    async def __aenter__(self):
        """Initialize resource"""
        self.resource = await self._create_resource()
        return self.resource
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup resource"""
        if self.resource:
            await self._cleanup_resource()
    
    async def _create_resource(self):
        """Create the managed resource"""
        # Implementation specific to resource type
        pass
    
    async def _cleanup_resource(self):
        """Cleanup the managed resource"""
        # Implementation specific to resource type
        pass
```

### **Configuration Management**
```python
class ConfigManager:
    """Centralized configuration management"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load configuration from file"""
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def get(self, key: str, default=None):
        """Get configuration value"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_database_config(self) -> Dict:
        """Get database configuration"""
        return {
            'host': self.get('database.host'),
            'port': self.get('database.port'),
            'user': self.get('database.user'),
            'password': self.get('database.password'),
            'database': self.get('database.name')
        }
```

### **Logging Patterns**
```python
import logging
import json
from datetime import datetime

class VectorFlowLogger:
    """Structured logging for VectorFlow"""
    
    def __init__(self, name: str, level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Add structured formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def log_market_event(self, event_type: str, data: Dict, level: str = "INFO"):
        """Log market event with structured data"""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'data': data
        }
        
        getattr(self.logger, level.lower())(
            f"Market Event: {json.dumps(log_data)}"
        )
    
    def log_performance(self, operation: str, duration_ms: float, level: str = "INFO"):
        """Log performance metrics"""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'duration_ms': duration_ms
        }
        
        getattr(self.logger, level.lower())(
            f"Performance: {json.dumps(log_data)}"
        )
```

## 🚨 **ERROR HANDLING PATTERNS**

### **Graceful Degradation**
```python
class GracefulDegradation:
    """Handle service failures gracefully"""
    
    def __init__(self, fallback_strategy: Callable):
        self.fallback_strategy = fallback_strategy
        self.logger = logging.getLogger(__name__)
    
    async def execute_with_fallback(self, primary_operation: Callable, *args, **kwargs):
        """Execute primary operation with fallback"""
        try:
            return await primary_operation(*args, **kwargs)
        except Exception as e:
            self.logger.warning(f"Primary operation failed: {e}")
            self.logger.info("Using fallback strategy")
            return await self.fallback_strategy(*args, **kwargs)
```

### **Retry Pattern**
```python
import asyncio
from typing import Callable, Any

class RetryHandler:
    """Handle retries with exponential backoff"""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.logger = logging.getLogger(__name__)
    
    async def execute_with_retry(self, operation: Callable, *args, **kwargs) -> Any:
        """Execute operation with retry logic"""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return await operation(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                if attempt < self.max_retries:
                    delay = self.base_delay * (2 ** attempt)
                    self.logger.warning(
                        f"Attempt {attempt + 1} failed: {e}. "
                        f"Retrying in {delay} seconds..."
                    )
                    await asyncio.sleep(delay)
                else:
                    self.logger.error(f"All {self.max_retries + 1} attempts failed")
                    raise last_exception
```

## 📊 **PERFORMANCE PATTERNS**

### **Connection Pooling**
```python
class ConnectionPool:
    """Manage database connection pool"""
    
    def __init__(self, pool_config: Dict):
        self.config = pool_config
        self.pool = None
    
    async def initialize(self):
        """Initialize connection pool"""
        self.pool = await asyncpg.create_pool(
            host=self.config['host'],
            port=self.config['port'],
            user=self.config['user'],
            password=self.config['password'],
            database=self.config['database'],
            min_size=self.config.get('min_size', 5),
            max_size=self.config.get('max_size', 20)
        )
    
    async def get_connection(self):
        """Get connection from pool"""
        if not self.pool:
            await self.initialize()
        return await self.pool.acquire()
    
    async def release_connection(self, conn):
        """Release connection back to pool"""
        if self.pool:
            await self.pool.release(conn)
```

### **Caching Strategy**
```python
class CacheManager:
    """Multi-level caching strategy"""
    
    def __init__(self):
        self.local_cache = {}
        self.redis_client = None
        self.logger = logging.getLogger(__name__)
    
    async def get(self, key: str, ttl: int = 300):
        """Get value from cache hierarchy"""
        # Try local cache first
        if key in self.local_cache:
            return self.local_cache[key]
        
        # Try Redis
        if self.redis_client:
            try:
                cached = await self.redis_client.get(key)
                if cached:
                    data = json.loads(cached)
                    self.local_cache[key] = data
                    return data
            except Exception as e:
                self.logger.warning(f"Redis cache failed: {e}")
        
        return None
    
    async def set(self, key: str, value: Any, ttl: int = 300):
        """Set value in cache hierarchy"""
        # Set in local cache
        self.local_cache[key] = value
        
        # Set in Redis
        if self.redis_client:
            try:
                await self.redis_client.setex(key, ttl, json.dumps(value))
            except Exception as e:
                self.logger.warning(f"Redis cache set failed: {e}")
```

## 🔄 **TESTING PATTERNS**

### **Async Testing**
```python
import pytest
import asyncio

class TestBase:
    """Base class for async tests"""
    
    @pytest.fixture(autouse=True)
    def setup_event_loop(self):
        """Setup event loop for async tests"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        yield
        self.loop.close()
    
    def run_async(self, coro):
        """Run async coroutine in test"""
        return self.loop.run_until_complete(coro)

class TestMarketDataService(TestBase):
    """Test market data service"""
    
    def test_data_collection(self):
        """Test market data collection"""
        async def test_coro():
            service = MarketDataService()
            data = await service.collect_data("BTCUSDT")
            assert data is not None
            assert 'price' in data
        
        self.run_async(test_coro())
```

## 🎯 **DEPLOYMENT PATTERNS**

### **Health Checks**
```python
class HealthChecker:
    """Service health monitoring"""
    
    def __init__(self, services: List[str]):
        self.services = services
        self.logger = logging.getLogger(__name__)
    
    async def check_health(self) -> Dict:
        """Check health of all services"""
        health_status = {}
        
        for service in self.services:
            try:
                status = await self._check_service_health(service)
                health_status[service] = status
            except Exception as e:
                health_status[service] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
        
        return health_status
    
    async def _check_service_health(self, service: str) -> Dict:
        """Check individual service health"""
        # Implementation specific to service type
        pass
```

---

**🎯 These patterns ensure maintainable, scalable, and reliable code**
**🤖 Designed for seamless AI model handovers and continuous development**
