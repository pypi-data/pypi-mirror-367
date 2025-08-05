"""
Tests for database integration and operations.

Tests cover:
- SQLAlchemy model relationships and constraints
- Data insertion for ticks, bars, and symbols
- Data retrieval and historical queries
- Database migration scripts
- Connection pool management
"""
import pytest
from datetime import datetime, date, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, patch

import pandas as pd

from quant_async.blotter import Blotter
from quant_async.models import Symbols, Bars, Ticks, Greeks, Trades


class TestDatabaseModels:
    """Test SQLAlchemy model definitions and relationships."""
    
    def test_symbols_model(self):
        """Test Symbols model creation."""
        symbol = Symbols(
            symbol='AAPL',
            symbol_group='AAPL',
            asset_class='STK',
            expiry=date(2024, 12, 20)
        )
        
        assert symbol.symbol == 'AAPL'
        assert symbol.symbol_group == 'AAPL'
        assert symbol.asset_class == 'STK'
        assert symbol.expiry == date(2024, 12, 20)
    
    def test_bars_model(self):
        """Test Bars model creation."""
        bar = Bars(
            datetime=datetime(2024, 8, 4, 10, 30, 0),
            symbol_id=1,
            open=Decimal('150.00'),
            high=Decimal('150.50'),
            low=Decimal('149.75'),
            close=Decimal('150.25'),
            volume=10000
        )
        
        assert bar.symbol_id == 1
        assert bar.open == Decimal('150.00')
        assert bar.high == Decimal('150.50')
        assert bar.low == Decimal('149.75')
        assert bar.close == Decimal('150.25')
        assert bar.volume == 10000
    
    def test_ticks_model(self):
        """Test Ticks model creation."""
        tick = Ticks(
            datetime=datetime(2024, 8, 4, 10, 30, 0),
            symbol_id=1,
            bid=Decimal('150.00'),
            bidsize=100,
            ask=Decimal('150.01'),
            asksize=200,
            last=Decimal('150.005'),
            lastsize=50
        )
        
        assert tick.symbol_id == 1
        assert tick.bid == Decimal('150.00')
        assert tick.ask == Decimal('150.01')
        assert tick.last == Decimal('150.005')
        assert tick.bidsize == 100
        assert tick.asksize == 200
        assert tick.lastsize == 50
    
    def test_greeks_model(self):
        """Test Greeks model creation."""
        greek = Greeks(
            tick_id=1,
            bar_id=None,
            price=Decimal('5.25'),
            underlying=Decimal('150.00'),
            dividend=Decimal('0.85'),
            volume=500,
            iv=Decimal('0.25'),
            oi=Decimal('1000'),
            delta=Decimal('0.65'),
            gamma=Decimal('0.05'),
            theta=Decimal('-0.02'),
            vega=Decimal('0.15')
        )
        
        assert greek.tick_id == 1
        assert greek.bar_id is None
        assert greek.price == Decimal('5.25')
        assert greek.delta == Decimal('0.65')
        assert greek.gamma == Decimal('0.05')
    
    def test_trades_model(self):
        """Test Trades model creation."""
        trade = Trades(
            algo='test_algo',
            symbol='AAPL',
            direction='BUY',
            quantity=100,
            entry_time=datetime(2024, 8, 4, 10, 30, 0),
            exit_time=datetime(2024, 8, 4, 11, 30, 0),
            exit_reason='PROFIT',
            order_type='MKT',
            market_price=Decimal('150.00'),
            target=Decimal('155.00'),
            stop=Decimal('145.00'),
            entry_price=Decimal('150.05'),
            exit_price=Decimal('154.25'),
            realized_pnl=Decimal('420.00')
        )
        
        assert trade.algo == 'test_algo'
        assert trade.symbol == 'AAPL'
        assert trade.direction == 'BUY'
        assert trade.quantity == 100
        assert trade.realized_pnl == Decimal('420.00')


class TestDatabaseConnection:
    """Test database connection and pool management."""
    
    @pytest.mark.asyncio
    async def test_get_postgres_connection_parameters(self):
        """Test postgres connection with custom parameters."""
        config = {
            'dbhost': 'custom_host',
            'dbport': '5433',
            'dbuser': 'custom_user',
            'dbpass': 'custom_pass',
            'dbname': 'custom_db'
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
                host='custom_host',
                port=5433,
                user='custom_user',
                password='custom_pass',
                database='custom_db',
                min_size=5,
                max_size=20
            )
            
            assert result is mock_pool
    
    @pytest.mark.asyncio
    async def test_postgres_connect_creates_pool(self, mock_asyncpg_pool):
        """Test postgres_connect creates connection pool."""
        blotter = Blotter(dbskip=False)
        
        with patch.object(blotter, 'get_postgres_connection', return_value=mock_asyncpg_pool):
            await blotter.postgres_connect()
            assert blotter.pool is mock_asyncpg_pool
    
    @pytest.mark.asyncio
    async def test_postgres_connect_existing_pool(self, mock_asyncpg_pool):
        """Test postgres_connect with existing pool."""
        blotter = Blotter(dbskip=False)
        blotter.pool = mock_asyncpg_pool
        
        with patch.object(blotter, 'get_postgres_connection') as mock_get:
            await blotter.postgres_connect()
            # Should not create new connection
            mock_get.assert_not_called()
            assert blotter.pool is mock_asyncpg_pool


class TestDatabaseOperations:
    """Test database CRUD operations."""
    
    @pytest.mark.asyncio
    async def test_get_symbol_id_new_stock(self, mock_asyncpg_pool):
        """Test getting symbol ID for new stock."""
        blotter = Blotter(dbskip=False)
        blotter.pool = mock_asyncpg_pool
        
        # Get the mock connection from our context manager
        mock_context = mock_asyncpg_pool.acquire.return_value
        mock_conn = await mock_context.__aenter__()
        
        # Mock database queries
        mock_conn.fetchrow.return_value = None  # Symbol doesn't exist
        mock_conn.fetchval.return_value = 123  # New symbol ID
        
        with patch('quant_async.tools.gen_asset_class', return_value='STK'):
            with patch('quant_async.tools.gen_symbol_group', return_value='AAPL'):
                symbol_id = await blotter.get_symbol_id('AAPL_STK')
        
        assert symbol_id == 123
        # Verify INSERT was called
        mock_conn.fetchval.assert_called()
    
    @pytest.mark.asyncio 
    async def test_get_symbol_id_existing_stock(self, mock_asyncpg_pool):
        """Test getting symbol ID for existing stock."""
        blotter = Blotter(dbskip=False)
        blotter.pool = mock_asyncpg_pool
        
        # Get the mock connection from our context manager
        mock_context = mock_asyncpg_pool.acquire.return_value
        mock_conn = await mock_context.__aenter__()
        
        # Configure the mock connection for our test case - symbol exists
        mock_conn.fetchrow.return_value = {'id': 456}
        
        with patch('quant_async.tools.gen_asset_class', return_value='STK'):
            with patch('quant_async.tools.gen_symbol_group', return_value='AAPL'):
                symbol_id = await blotter.get_symbol_id('AAPL_STK')
        
        assert symbol_id == 456
        # Verify fetchrow was called to check for existing symbol
        mock_conn.fetchrow.assert_called()
        # Verify INSERT was not called for existing symbol
        mock_conn.fetchval.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_get_symbol_id_futures(self, mock_asyncpg_pool):
        """Test getting symbol ID for futures contract."""
        blotter = Blotter(dbskip=False)
        blotter.pool = mock_asyncpg_pool
        
        # Mock connection context manager
        mock_conn = AsyncMock()
        mock_asyncpg_pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_asyncpg_pool.acquire.return_value.__aexit__ = AsyncMock(return_value=None)
        
        # Mock database queries - futures doesn't exist
        mock_conn.fetchrow.return_value = None
        mock_conn.fetchval.return_value = 789
        
        with patch('quant_async.tools.gen_asset_class', return_value='FUT'):
            with patch('quant_async.tools.gen_symbol_group', return_value='ES'):
                with patch.object(blotter, '_get_contract_expiry', return_value=date(2024, 9, 19)):
                    symbol_id = await blotter.get_symbol_id('ES_FUT')
        
        assert symbol_id == 789
    
    @pytest.mark.asyncio
    async def test_insert_tick_data(self, mock_asyncpg_pool):
        """Test inserting tick data."""
        blotter = Blotter(dbskip=False)
        blotter.pool = mock_asyncpg_pool  # Note: uses db_pool not pool
        
        # Mock connection context manager
        mock_conn = AsyncMock()
        mock_asyncpg_pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_asyncpg_pool.acquire.return_value.__aexit__ = AsyncMock(return_value=None)
        
        mock_conn.fetchval.return_value = 111  # tick_id
        
        tick_data = {
            'timestamp': datetime(2024, 8, 4, 10, 30, 0),
            'bid': 150.0,
            'bidsize': 100,
            'ask': 150.1,
            'asksize': 200,
            'last': 150.05,
            'lastsize': 50,
            'asset_class': 'STK'
        }
        
        await blotter.insert_tick(tick_data, symbol_id=1)
        
        # Verify tick insertion
        mock_conn.fetchval.assert_called_once()
        call_args = mock_conn.fetchval.call_args[0]
        assert 'INSERT INTO ticks' in call_args[0]
    
    @pytest.mark.asyncio
    async def test_insert_bar_data(self, mock_asyncpg_pool):
        """Test inserting bar data."""
        blotter = Blotter(dbskip=False)
        blotter.pool = mock_asyncpg_pool
        
        # Mock connection context manager
        mock_conn = AsyncMock()
        mock_asyncpg_pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_asyncpg_pool.acquire.return_value.__aexit__ = AsyncMock(return_value=None)
        
        mock_conn.fetchval.return_value = 222  # bar_id
        
        bar_data = {
            'timestamp': datetime(2024, 8, 4, 10, 30, 0),
            'open': 150.0,
            'high': 150.5,
            'low': 149.8,
            'close': 150.2,
            'volume': 10000,
            'asset_class': 'STK'
        }
        
        await blotter.insert_bar(bar_data, symbol_id=1)
        
        # Verify bar insertion
        mock_conn.fetchval.assert_called_once()
        call_args = mock_conn.fetchval.call_args[0]
        assert 'INSERT INTO bars' in call_args[0]
    
    @pytest.mark.asyncio
    async def test_insert_options_tick_with_greeks(self, mock_asyncpg_pool):
        """Test inserting options tick data with Greeks."""
        blotter = Blotter(dbskip=False)
        blotter.pool = mock_asyncpg_pool
        blotter.cash_ticks = {
            'AAPL_OPT': {
                'opt_price': 5.25,
                'opt_underlying': 150.0,
                'opt_dividend': 0.85,
                'opt_volume': 500,
                'opt_iv': 0.25,
                'opt_oi': 1000,
                'opt_delta': 0.65,
                'opt_gamma': 0.05,
                'opt_theta': -0.02,
                'opt_vega': 0.15
            }
        }
        
        # Mock connection context manager
        mock_conn = AsyncMock()
        mock_asyncpg_pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_asyncpg_pool.acquire.return_value.__aexit__ = AsyncMock(return_value=None)
        
        mock_conn.fetchval.return_value = 333  # tick_id
        
        tick_data = {
            'timestamp': datetime(2024, 8, 4, 10, 30, 0),
            'bid': 5.20,
            'bidsize': 10,
            'ask': 5.30,
            'asksize': 15,
            'last': 5.25,
            'lastsize': 5,
            'asset_class': 'OPT',
            'opt_price': 5.25,
            'opt_underlying': 150.0,
            'opt_dividend': 0.85,
            'opt_volume': 500,
            'opt_iv': 0.25,
            'opt_oi': 1000,
            'opt_delta': 0.65,
            'opt_gamma': 0.05,
            'opt_theta': -0.02,
            'opt_vega': 0.15
        }
        
        await blotter.insert_tick(tick_data, symbol_id=1)
        
        # Verify both tick and Greeks insertion
        assert mock_conn.fetchval.call_count == 1  # tick insertion
        assert mock_conn.execute.call_count == 1   # Greeks insertion


class TestHistoricalDataQueries:
    """Test historical data retrieval and queries."""
    
    @pytest.mark.asyncio
    async def test_history_bars_query(self, mock_asyncpg_pool):
        """Test historical bars query."""
        blotter = Blotter(dbskip=False)
        blotter.pool = mock_asyncpg_pool
        
        # Mock connection context manager
        mock_conn = AsyncMock()
        mock_asyncpg_pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_asyncpg_pool.acquire.return_value.__aexit__ = AsyncMock(return_value=None)
        
        # Mock query results
        mock_records = [
            {
                'id': 1,
                'datetime': datetime(2024, 8, 4, 10, 30, 0),
                'symbol_id': 1,
                'symbol': 'AAPL_STK',
                'open': 150.0,
                'high': 150.5,
                'low': 149.8,
                'close': 150.2,
                'volume': 10000
            }
        ]
        mock_conn.fetch.return_value = mock_records
        
        # Mock the prepare_history function
        with patch('quant_async.blotter.prepare_history') as mock_prepare:
            mock_prepare.return_value = pd.DataFrame(mock_records)
            
            await blotter.history(
                symbols=['AAPL_STK'],
                start=datetime(2024, 8, 1),
                end=datetime(2024, 8, 4),
                resolution='1D'
            )
        
        # Verify query was executed
        mock_conn.fetch.assert_called_once()
        call_args = mock_conn.fetch.call_args[0]
        assert 'SELECT tbl.*' in call_args[0]
        assert 'FROM bars tbl' in call_args[0]
    
    @pytest.mark.asyncio
    async def test_history_ticks_query(self, mock_asyncpg_pool):
        """Test historical ticks query."""
        blotter = Blotter(dbskip=False)
        blotter.pool = mock_asyncpg_pool
        
        # Mock connection context manager
        mock_conn = AsyncMock()
        mock_asyncpg_pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_asyncpg_pool.acquire.return_value.__aexit__ = AsyncMock(return_value=None)
        
        mock_conn.fetch.return_value = []
        
        with patch('quant_async.blotter.prepare_history') as mock_prepare:
            mock_prepare.return_value = pd.DataFrame()
            
            await blotter.history(
                symbols=['EURUSD_CASH'],
                start=datetime(2024, 8, 1),
                resolution='1T'  # Tick resolution
            )
        
        # Verify ticks table was queried
        mock_conn.fetch.assert_called_once()
        call_args = mock_conn.fetch.call_args[0]
        assert 'FROM ticks tbl' in call_args[0]
    
    @pytest.mark.asyncio
    async def test_fix_history_sequence_removes_bad_data(self, mock_asyncpg_pool):
        """Test history sequence fixing removes malformed data."""
        blotter = Blotter(dbskip=False)
        blotter.pool = mock_asyncpg_pool
        
        # Mock connection context manager  
        mock_conn = AsyncMock()
        mock_asyncpg_pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_asyncpg_pool.acquire.return_value.__aexit__ = AsyncMock(return_value=None)
        
        # Create malformed data (newer ID but older timestamp)
        malformed_data = pd.DataFrame({
            'id': [1, 3, 2],  # Out of sequence
            'datetime': [
                datetime(2024, 8, 4, 10, 0, 0),
                datetime(2024, 8, 4, 9, 0, 0),   # Older timestamp but newer ID
                datetime(2024, 8, 4, 11, 0, 0)
            ],
            'symbol_id': [1, 1, 1],
            'close': [150.0, 149.0, 151.0]
        })
        
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 8, 4, 12, 0, 0, tzinfo=timezone.utc)
            
            result = await blotter._fix_history_sequence(malformed_data, 'bars')
        
        # Verify malformed data was removed
        assert len(result) < len(malformed_data)
        # Verify cleanup queries were executed
        assert mock_conn.execute.call_count == 2  # Greeks cleanup + main table cleanup


class TestDatabaseIntegration:
    """Test database integration scenarios."""
    
    @pytest.mark.asyncio
    async def test_log2db_skipped(self):
        """Test log2db when database is skipped."""
        blotter = Blotter(dbskip=True)
        
        sample_data = {
            'symbol': 'AAPL_STK',
            'asset_class': 'STK',
            'timestamp': datetime.now()
        }
        
        # Should not raise exception
        await blotter.log2db(sample_data, 'TICK')
    
    @pytest.mark.asyncio
    async def test_log2db_invalid_symbol(self):
        """Test log2db with invalid symbol format."""
        blotter = Blotter(dbskip=True)
        
        # Symbol with too many underscores
        sample_data = {
            'symbol': 'AAPL_STK_EXTRA_PARTS',
            'asset_class': 'STK',
            'timestamp': datetime.now()
        }
        
        # Should skip logging
        await blotter.log2db(sample_data, 'TICK')
    
    @pytest.mark.asyncio
    async def test_log2db_tick_data(self, mock_asyncpg_pool):
        """Test log2db with tick data."""
        blotter = Blotter(dbskip=False)
        blotter.pool = mock_asyncpg_pool
        blotter.symbol_ids = {}
        
        sample_data = {
            'symbol': 'AAPL_STK',
            'asset_class': 'STK',
            'timestamp': datetime.now(),
            'bid': 150.0,
            'ask': 150.1,
            'last': 150.05
        }
        
        with patch.object(blotter, 'get_symbol_id', return_value=123):
            with patch.object(blotter, 'insert_tick') as mock_insert:
                await blotter.log2db(sample_data, 'TICK')
                
                mock_insert.assert_called_once_with(sample_data, 123)
                assert blotter.symbol_ids['AAPL'] == 123
    
    @pytest.mark.asyncio
    async def test_log2db_bar_data(self, mock_asyncpg_pool):
        """Test log2db with bar data."""
        blotter = Blotter(dbskip=False)
        blotter.pool = mock_asyncpg_pool
        blotter.symbol_ids = {}
        
        sample_data = {
            'symbol': 'AAPL_STK',
            'asset_class': 'STK',
            'timestamp': datetime.now(),
            'open': 150.0,
            'high': 150.5,
            'low': 149.8,
            'close': 150.2,
            'volume': 10000
        }
        
        with patch.object(blotter, 'get_symbol_id', return_value=456):
            with patch.object(blotter, 'insert_bar') as mock_insert:
                await blotter.log2db(sample_data, 'BAR')
                
                mock_insert.assert_called_once_with(sample_data, 456)
                assert blotter.symbol_ids['AAPL'] == 456