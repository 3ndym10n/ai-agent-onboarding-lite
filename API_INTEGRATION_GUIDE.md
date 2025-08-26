# 🔌 VectorFlow API Integration Guide

**External Service Integrations and API Management**

## 🎯 **CORE INTEGRATIONS**

### **1. Multi-Exchange APIs**

#### **Binance API Integration**
```python
class BinanceAPI:
    """Binance API integration with rate limiting and error handling"""
    
    def __init__(self, api_key: str, api_secret: str):
        self.client = Client(api_key, api_secret)
        self.rate_limiter = RateLimiter(max_requests=1200, time_window=60)
    
    async def get_klines(self, symbol: str, interval: str, limit: int = 500):
        """Get candlestick data with rate limiting"""
        await self.rate_limiter.acquire()
        try:
            klines = self.client.get_klines(
                symbol=symbol,
                interval=interval,
                limit=limit
            )
            return self._format_klines(klines)
        except Exception as e:
            logger.error(f"Binance API error: {e}")
            raise
    
    async def get_order_book(self, symbol: str, limit: int = 100):
        """Get order book data"""
        await self.rate_limiter.acquire()
        try:
            book = self.client.get_order_book(symbol=symbol, limit=limit)
            return self._format_order_book(book)
        except Exception as e:
            logger.error(f"Binance order book error: {e}")
            raise
```

#### **Bybit API Integration**
```python
class BybitAPI:
    """Bybit API integration with WebSocket support"""
    
    def __init__(self, api_key: str, api_secret: str):
        self.client = HTTP(api_key, api_secret)
        self.ws_client = WebSocket(api_key, api_secret)
    
    async def get_kline_data(self, symbol: str, interval: str, limit: int = 200):
        """Get kline data from Bybit"""
        try:
            response = self.client.Kline.Kline_get(
                symbol=symbol,
                interval=interval,
                limit=limit
            ).result()
            return self._format_bybit_klines(response)
        except Exception as e:
            logger.error(f"Bybit API error: {e}")
            raise
    
    async def subscribe_orderbook(self, symbol: str, callback):
        """Subscribe to orderbook updates"""
        try:
            self.ws_client.orderbook_stream(
                symbol=symbol,
                callback=callback
            )
        except Exception as e:
            logger.error(f"Bybit WebSocket error: {e}")
            raise
```

### **2. Grok AI Integration**

#### **Playbook Generation**
```python
class GrokAIClient:
    """Grok AI integration for trading playbook generation"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.grok.ai/v1"
        self.session = aiohttp.ClientSession()
    
    async def generate_playbook(self, market_context: Dict, signal_data: Dict) -> Dict:
        """Generate trading playbook using Grok AI"""
        prompt = self._build_playbook_prompt(market_context, signal_data)
        
        try:
            async with self.session.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "grok-beta",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a professional cryptocurrency trading analyst. Generate concise, actionable trading playbooks based on market data and technical analysis."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "max_tokens": 500,
                    "temperature": 0.3
                }
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return self._parse_playbook_response(result)
                else:
                    raise Exception(f"Grok AI API error: {response.status}")
        except Exception as e:
            logger.error(f"Grok AI integration error: {e}")
            raise
    
    def _build_playbook_prompt(self, market_context: Dict, signal_data: Dict) -> str:
        """Build prompt for playbook generation"""
        return f"""
        Market Context:
        - Symbol: {market_context.get('symbol', 'Unknown')}
        - Current Price: {market_context.get('price', 'Unknown')}
        - 24h Change: {market_context.get('change_24h', 'Unknown')}
        - Volume: {market_context.get('volume', 'Unknown')}
        
        Signal Analysis:
        - TPO Analysis: {signal_data.get('tpo_analysis', {})}
        - Regime Detection: {signal_data.get('regime_detection', {})}
        - Trap Detection: {signal_data.get('trap_detection', {})}
        - OI Analysis: {signal_data.get('oi_analysis', {})}
        
        Generate a concise trading playbook with:
        1. Entry strategy
        2. Risk management
        3. Target levels
        4. Confidence score (0-100)
        """
```

### **3. VectorBT Integration**

#### **Backtesting Engine**
```python
class VectorBTBacktester:
    """VectorBT integration for strategy backtesting"""
    
    def __init__(self):
        self.engine = None
    
    async def run_backtest(self, strategy_config: Dict, price_data: pd.DataFrame) -> Dict:
        """Run backtest using VectorBT"""
        try:
            # Initialize VectorBT engine
            self.engine = vbt.BinanceData.fetch(
                symbol=strategy_config['symbol'],
                start=strategy_config['start_date'],
                end=strategy_config['end_date'],
                timeframe=strategy_config['timeframe']
            )
            
            # Define strategy
            strategy = self._define_strategy(strategy_config)
            
            # Run backtest
            portfolio = strategy.run()
            
            # Calculate metrics
            metrics = self._calculate_metrics(portfolio)
            
            return {
                'portfolio': portfolio,
                'metrics': metrics,
                'trades': self._extract_trades(portfolio)
            }
        except Exception as e:
            logger.error(f"VectorBT backtest error: {e}")
            raise
    
    def _define_strategy(self, config: Dict):
        """Define trading strategy for VectorBT"""
        # Implementation depends on strategy type
        pass
    
    def _calculate_metrics(self, portfolio) -> Dict:
        """Calculate performance metrics"""
        return {
            'total_return': portfolio.total_return(),
            'sharpe_ratio': portfolio.sharpe_ratio(),
            'max_drawdown': portfolio.max_drawdown(),
            'win_rate': portfolio.win_rate(),
            'profit_factor': portfolio.profit_factor()
        }
```

## 🔧 **API MANAGEMENT**

### **Rate Limiting**
```python
class RateLimiter:
    """Generic rate limiter for API calls"""
    
    def __init__(self, max_requests: int, time_window: int):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = deque()
        self.lock = asyncio.Lock()
    
    async def acquire(self):
        """Acquire rate limit slot"""
        async with self.lock:
            now = time.time()
            
            # Remove expired requests
            while self.requests and now - self.requests[0] > self.time_window:
                self.requests.popleft()
            
            # Check if we can make a request
            if len(self.requests) >= self.max_requests:
                wait_time = self.time_window - (now - self.requests[0])
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
            
            # Add current request
            self.requests.append(now)
```

### **Error Handling**
```python
class APIErrorHandler:
    """Centralized API error handling"""
    
    def __init__(self):
        self.error_counts = defaultdict(int)
        self.circuit_breakers = {}
    
    async def handle_api_call(self, api_name: str, call_func: Callable, *args, **kwargs):
        """Handle API call with error management"""
        try:
            return await call_func(*args, **kwargs)
        except Exception as e:
            self.error_counts[api_name] += 1
            
            if self.error_counts[api_name] > 5:
                logger.error(f"Too many errors for {api_name}, activating circuit breaker")
                self.circuit_breakers[api_name] = time.time() + 300  # 5 minutes
            
            raise e
    
    def is_circuit_open(self, api_name: str) -> bool:
        """Check if circuit breaker is open"""
        if api_name in self.circuit_breakers:
            if time.time() < self.circuit_breakers[api_name]:
                return True
            else:
                del self.circuit_breakers[api_name]
        return False
```

## 🔄 **DATA SYNCHRONIZATION**

### **Multi-Exchange Data Sync**
```python
class DataSynchronizer:
    """Synchronize data across multiple exchanges"""
    
    def __init__(self, exchanges: List[str]):
        self.exchanges = exchanges
        self.sync_interval = 5  # seconds
        self.last_sync = {}
    
    async def sync_market_data(self, symbol: str) -> Dict:
        """Synchronize market data across exchanges"""
        tasks = []
        for exchange in self.exchanges:
            if self._should_sync(exchange, symbol):
                task = self._fetch_exchange_data(exchange, symbol)
                tasks.append(task)
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return self._merge_exchange_data(results)
        
        return {}
    
    def _should_sync(self, exchange: str, symbol: str) -> bool:
        """Check if we should sync this exchange/symbol"""
        key = f"{exchange}:{symbol}"
        last_time = self.last_sync.get(key, 0)
        return time.time() - last_time > self.sync_interval
    
    async def _fetch_exchange_data(self, exchange: str, symbol: str) -> Dict:
        """Fetch data from specific exchange"""
        # Implementation depends on exchange
        pass
```

## 🚨 **SECURITY CONSIDERATIONS**

### **API Key Management**
```python
class APIKeyManager:
    """Secure API key management"""
    
    def __init__(self, key_file: str = "config/api_keys.json"):
        self.key_file = key_file
        self.keys = self._load_keys()
    
    def _load_keys(self) -> Dict:
        """Load API keys from secure file"""
        try:
            with open(self.key_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"API key file not found: {self.key_file}")
            return {}
    
    def get_key(self, service: str) -> str:
        """Get API key for service"""
        if service not in self.keys:
            raise ValueError(f"No API key found for service: {service}")
        return self.keys[service]
    
    def validate_key(self, service: str, key: str) -> bool:
        """Validate API key"""
        # Implementation depends on service
        pass
```

---

**🎯 This guide ensures reliable integration with external services**
**🤖 Designed for seamless AI model handovers and continuous development**
