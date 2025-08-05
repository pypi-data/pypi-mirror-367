"""
Tests for Blotter functionality.

Tests cover:
- Blotter initialization and configuration
- Database connection and connection pooling
- ZeroMQ socket creation and lifecycle
- Symbol file hot-reloading mechanism
- Market data event handlers (on_quote_received, on_tick_received)
- Interactive Brokers connection handling
"""
import pytest
import asyncio
import pandas as pd
from unittest.mock import AsyncMock, MagicMock, patch, mock_open

import aiozmq
import zmq

from quant_async.blotter import Blotter


class TestBlotterInitialization:
    """Test Blotter initialization and configuration."""
    
    def test_blotter_default_initialization(self):
        """Test Blotter initializes with proper defaults."""
        blotter = Blotter(dbskip=True)
        
        assert blotter.name is not None
        assert blotter.args['ibport'] == 4001
        assert blotter.args['ibhost'] == 'localhost'
        assert blotter.args['ibclient'] == 996
        assert blotter.args['dbskip'] is True
        assert blotter.args['zmqport'] == '12345'
        assert blotter.socket is None
        assert blotter.pool is None
    
    def test_blotter_custom_initialization(self):
        """Test Blotter initializes with custom parameters."""
        config = {
            'name': 'custom_blotter',
            'ibhost': '192.168.1.100',
            'ibport': 4002,
            'ibclient': 997,
            'dbname': 'custom_db',
            'zmqport': '54321',
            'orderbook': True
        }
        
        blotter = Blotter(**config)
        
        assert blotter.name == 'custom_blotter'
        assert blotter.args['ibhost'] == '192.168.1.100'
        assert blotter.args['ibport'] == 4002
        assert blotter.args['ibclient'] == 997
        assert blotter.args['dbname'] == 'custom_db'
        assert blotter.args['zmqport'] == '54321'
        assert blotter.args['orderbook'] is True

    def test_blotter_auto_name_detection(self):
        """Test automatic name detection from class name."""
        class CustomBlotter(Blotter):
            pass
        
        blotter = CustomBlotter(dbskip=True)
        assert blotter.name == 'customblotter'


class TestBlotterDatabase:
    """Test database connection and operations."""
    
    @pytest.mark.asyncio
    async def test_postgres_connect_skip(self):
        """Test postgres connection when dbskip=True."""
        blotter = Blotter(dbskip=True)
        await blotter.postgres_connect()
        assert blotter.pool is None
    
    @pytest.mark.asyncio
    async def test_postgres_connect_success(self, mock_asyncpg_pool):
        """Test successful postgres connection."""
        blotter = Blotter(dbskip=False)
        
        # Mock the get_postgres_connection method to return our mock pool
        with patch.object(blotter, 'get_postgres_connection', return_value=mock_asyncpg_pool):
            await blotter.postgres_connect()
            assert blotter.pool is not None
    
    @pytest.mark.asyncio
    async def test_postgres_connect_already_connected(self, mock_asyncpg_pool):
        """Test postgres connection when already connected."""
        blotter = Blotter(dbskip=False)
        blotter.pool = mock_asyncpg_pool
        
        await blotter.postgres_connect()
        # Should not create new connection
        assert blotter.pool is mock_asyncpg_pool
    
    @pytest.mark.asyncio
    async def test_get_postgres_connection_config(self):
        """Test postgres connection configuration."""
        config = {
            'dbhost': 'test_host',
            'dbport': '5433',
            'dbuser': 'test_user',
            'dbpass': 'test_pass',
            'dbname': 'test_db'
        }
        
        blotter = Blotter(**config)
        
        # Create a mock pool object that will be returned
        mock_pool = AsyncMock()
        
        # Mock asyncpg.create_pool as an async function
        with patch('quant_async.blotter.asyncpg.create_pool', new_callable=AsyncMock) as mock_create_pool:
            mock_create_pool.return_value = mock_pool
            result = await blotter.get_postgres_connection()
            
            # Verify the result is our mock pool
            assert result is mock_pool
            
            # Verify connection parameters
            mock_create_pool.assert_called_once_with(
                host='test_host',
                port=5433,
                user='test_user',
                password='test_pass',
                database='test_db',
                min_size=5,
                max_size=20
            )


class TestBlotterZeroMQ:
    """Test ZeroMQ socket management."""
    
    @pytest.mark.asyncio
    async def test_zmq_socket_creation(self, mock_zmq_socket):
        """Test ZeroMQ socket creation in setup method."""
        blotter = Blotter(dbskip=True)
        
        with patch('quant_async.blotter.aiozmq.create_zmq_stream', return_value=mock_zmq_socket) as mock_create:
            # Directly test the ZMQ setup method
            await blotter._setup_zmq_with_monitoring()
        
        # Verify socket was created
        mock_create.assert_called_once_with(zmq.PUB, bind="tcp://*:12345")
        assert blotter.socket is mock_zmq_socket
    
    def test_broadcast_no_socket(self):
        """Test broadcast when socket is None."""
        blotter = Blotter(dbskip=True)
        blotter.socket = None
        
        # Should not raise exception
        blotter.broadcast({'test': 'data'}, 'TEST')
    
    def test_broadcast_success(self, mock_zmq_socket, sample_market_data):
        """Test successful message broadcasting."""
        blotter = Blotter(dbskip=True)
        blotter.socket = mock_zmq_socket
        
        blotter.broadcast(sample_market_data, 'QUOTE')
        
        # Verify message was serialized and sent
        mock_zmq_socket.write.assert_called_once()
        args = mock_zmq_socket.write.call_args[0][0]
        assert isinstance(args[0], bytes)  # Should be msgspec serialized
    
    def test_broadcast_error_handling(self, mock_zmq_socket, sample_market_data):
        """Test broadcast error handling."""
        blotter = Blotter(dbskip=True)
        blotter.socket = mock_zmq_socket
        mock_zmq_socket.write.side_effect = aiozmq.ZmqStreamClosed()
        
        # Should not raise exception
        blotter.broadcast(sample_market_data, 'QUOTE')


class TestBlotterSymbolManagement:
    """Test symbol file management and hot-reloading."""
    
    @pytest.mark.asyncio
    async def test_watch_symbols_file_not_exists(self, tmp_path):
        """Test symbol file watching when file doesn't exist."""
        symbols_file = tmp_path / "nonexistent.csv"
        # Ensure the parent directory exists
        symbols_file.parent.mkdir(parents=True, exist_ok=True)
        blotter = Blotter(symbols=str(symbols_file), dbskip=True)
        
        # Mock the infinite loop to run once
        with patch('asyncio.sleep', side_effect=[None, asyncio.CancelledError()]):
            with pytest.raises(asyncio.CancelledError):
                await blotter._watch_symbols_file()
        
        # File should be created
        assert symbols_file.exists()
        
        # Verify CSV structure
        df = pd.read_csv(symbols_file)
        expected_columns = ['symbol', 'sec_type', 'exchange', 'currency', 'expiry', 'strike', 'opt_type']
        assert list(df.columns) == expected_columns
    
    @pytest.mark.asyncio
    async def test_watch_symbols_file_empty(self, temp_symbols_file):
        """Test symbol file watching with empty file."""
        # Create empty file
        with open(temp_symbols_file, 'w') as f:
            f.write("")
        
        blotter = Blotter(symbols=temp_symbols_file, dbskip=True)
        blotter.ezib = MagicMock()
        
        # Mock the infinite loop to run once
        with patch('asyncio.sleep', side_effect=[None, None, asyncio.CancelledError()]):
            with pytest.raises(asyncio.CancelledError):
                await blotter._watch_symbols_file()
    
    @pytest.mark.asyncio
    async def test_watch_symbols_file_valid_data(self, temp_symbols_file):
        """Test symbol file watching with valid data."""
        blotter = Blotter(symbols=temp_symbols_file, dbskip=True)
        blotter.ezib = MagicMock()
        blotter.ezib.createContract = AsyncMock()
        blotter.ezib.requestMarketData = AsyncMock()
        blotter.ezib.contractString = MagicMock(return_value="AAPL_STK")
        
        # Mock the infinite loop to run twice
        with patch('asyncio.sleep', side_effect=[None, None, None, asyncio.CancelledError()]):
            with pytest.raises(asyncio.CancelledError):
                await blotter._watch_symbols_file()
        
        # Verify contracts were created and market data requested
        assert blotter.ezib.createContract.call_count >= 1
        assert blotter.ezib.requestMarketData.call_count >= 1

    def test_register_instruments_dict(self, temp_symbols_file):
        """Test registering instruments from dictionary."""
        # Ensure the parent directory exists
        import os
        os.makedirs(os.path.dirname(temp_symbols_file), exist_ok=True)
        blotter = Blotter(symbols=temp_symbols_file, dbskip=True)
        
        instruments = {
            'MSFT_STK': ('MSFT', 'STK', 'SMART', 'USD', '', '', ''),
            'GOOGL_STK': ('GOOGL', 'STK', 'SMART', 'USD', '', '', '')
        }
        
        blotter.register(instruments)
        
        # Verify instruments were added to CSV
        df = pd.read_csv(temp_symbols_file)
        symbols = df['symbol'].tolist()
        assert 'MSFT' in symbols
        assert 'GOOGL' in symbols
    
    def test_register_instruments_list(self, temp_symbols_file):
        """Test registering instruments from list."""
        # Ensure the parent directory exists
        import os
        os.makedirs(os.path.dirname(temp_symbols_file), exist_ok=True)
        blotter = Blotter(symbols=temp_symbols_file, dbskip=True)
        
        instruments = [
            ('TSLA', 'STK', 'SMART', 'USD', '', '', ''),
            ('META', 'STK', 'SMART', 'USD', '', '', '')
        ]
        
        blotter.register(instruments)
        
        # Verify instruments were added to CSV
        df = pd.read_csv(temp_symbols_file)
        symbols = df['symbol'].tolist()
        assert 'TSLA' in symbols
        assert 'META' in symbols


class TestBlotterEventHandlers:
    """Test market data event handlers."""
    
    def test_on_quote_received_stock(self, mock_ezib):
        """Test quote received handler for stocks."""
        blotter = Blotter(dbskip=True)
        blotter.ezib = mock_ezib
        blotter.socket = MagicMock()
        blotter.broadcast = MagicMock()
        
        # Setup mock data
        ticker_id = 1
        mock_ezib.tickerSymbol.return_value = "AAPL"
        mock_ezib.contracts[ticker_id].secType = "STK"
        
        # Create mock market data
        market_data = pd.DataFrame({
            'bid': [150.0],
            'bidsize': [100],
            'ask': [150.1],
            'asksize': [200],
            'last': [150.05],
            'lastsize': [50],
            'timestamp': [pd.Timestamp.now()],
            'volume': [1000]
        })
        mock_ezib.marketData[ticker_id] = market_data
        
        with patch('quant_async.tools.gen_symbol_group', return_value='AAPL'):
            with patch('quant_async.tools.gen_asset_class', return_value='STK'):
                with patch('quant_async.tools.to_decimal', side_effect=lambda x: float(x)):
                    blotter.on_quote_received(ticker_id)
        
        # Verify broadcast was called
        blotter.broadcast.assert_called()
    
    def test_on_tick_received(self):
        """Test tick received handler."""
        blotter = Blotter(dbskip=True)
        
        tick_data = {
            'last': 150.05,
            'lastsize': 50,
            'volume': 1000
        }
        
        # Should not raise exception
        blotter.on_tick_received(tick_data)
    
    @pytest.mark.asyncio
    async def test_on_orderbook_received(self, sample_orderbook_data):
        """Test orderbook received handler."""
        blotter = Blotter(dbskip=True)
        blotter.broadcast = AsyncMock()
        
        # Create mock ticker with DOM data
        mock_ticker = MagicMock()
        mock_ticker.domBids = [
            MagicMock(price=150.0, size=100, marketMaker='MM1'),
            MagicMock(price=149.99, size=200, marketMaker='MM2')
        ]
        mock_ticker.domAsks = [
            MagicMock(price=150.01, size=150, marketMaker='MM3'),
            MagicMock(price=150.02, size=300, marketMaker='MM4')
        ]
        
        await blotter.on_orderbook_received([mock_ticker])
        
        # Should not raise exception and should attempt broadcast
        # Note: broadcast is called asynchronously via asyncio.create_task


class TestBlotterConnectionManagement:
    """Test Interactive Brokers connection management."""
    
    @pytest.mark.asyncio
    async def test_blotter_file_running(self):
        """Test checking if blotter process is running."""
        with patch('asyncio.create_subprocess_shell') as mock_subprocess:
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (b'12345\n23456\n', b'')
            mock_subprocess.return_value = mock_process
            
            result = await Blotter._blotter_file_running()
            assert result is True
    
    @pytest.mark.asyncio
    async def test_blotter_file_not_running(self):
        """Test checking when blotter process is not running."""
        with patch('asyncio.create_subprocess_shell') as mock_subprocess:
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (b'', b'')
            mock_subprocess.return_value = mock_process
            
            result = await Blotter._blotter_file_running()
            assert result is False
    
    @pytest.mark.asyncio
    async def test_check_unique_blotter_no_existing(self):
        """Test unique blotter check when no existing instance."""
        blotter = Blotter(dbskip=True)
        
        with patch('quant_async.blotter.Blotter._blotter_file_running', return_value=False):
            with patch.object(blotter, '_write_cached_args') as mock_write:
                with patch('os.path.exists', return_value=False):
                    await blotter._check_unique_blotter()
                    mock_write.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_cached_args_operations(self):
        """Test cached args read/write operations."""
        blotter = Blotter(dbskip=True)
        
        # Test write
        with patch('builtins.open', mock_open()) as mock_file:
            with patch('pickle.dump') as mock_dump:
                with patch('os.chmod') as mock_chmod:
                    await blotter._write_cached_args()
                    mock_dump.assert_called_once_with(blotter.args, mock_file().__enter__())
                    mock_chmod.assert_called_once()
        
        # Test read
        test_args = {'test': 'value'}
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open()):
                with patch('pickle.load', return_value=test_args):
                    result = await blotter._read_cached_args()
                    assert result == test_args
        
        # Test remove
        with patch('os.path.exists', return_value=True):
            with patch('os.remove') as mock_remove:
                await blotter._remove_cached_args()
                mock_remove.assert_called_once()


class TestBlotterCLIArgs:
    """Test command-line argument parsing."""
    
    def test_load_cli_args_defaults(self):
        """Test CLI args with defaults."""
        blotter = Blotter(dbskip=True)
        
        with patch('sys.argv', ['blotter.py']):
            args = blotter.load_cli_args()
            # Should return empty dict when no args provided
            assert isinstance(args, dict)
    
    def test_load_cli_args_custom(self):
        """Test CLI args with custom values.""" 
        blotter = Blotter(dbskip=True)
        
        test_args = [
            'blotter.py',
            '--ibport', '4002',
            '--ibclient', '997',
            '--dbname', 'test_db',
            '--zmqport', '54321'
        ]
        
        with patch('sys.argv', test_args):
            args = blotter.load_cli_args()
            # CLI args are returned as strings by argparse
            assert args.get('ibport') == '4002'
            assert args.get('ibclient') == '997'
            assert args.get('dbname') == 'test_db'
            assert args.get('zmqport') == '54321'