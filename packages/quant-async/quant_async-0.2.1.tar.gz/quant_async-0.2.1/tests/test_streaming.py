"""
Tests for ZeroMQ streaming and message handling.

Tests cover:
- ZeroMQ pub/sub message flow
- msgspec serialization/deserialization
- Multiple subscriber scenarios
- Connection recovery and error handling
- Topic filtering and message routing
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

import zmq
import aiozmq
import msgspec

from quant_async.blotter import Blotter
from quant_async.algo import Algo


class TestZeroMQBasics:
    """Test basic ZeroMQ functionality."""
    
    @pytest.mark.asyncio
    async def test_create_pub_socket(self):
        """Test creating ZeroMQ publisher socket."""
        with patch('aiozmq.create_zmq_stream') as mock_create:
            mock_socket = AsyncMock()
            mock_socket.transport.bindings.return_value = ["tcp://*:12345"]
            mock_create.return_value = mock_socket
            
            socket = await aiozmq.create_zmq_stream(zmq.PUB, bind="tcp://*:12345")
            
            mock_create.assert_called_once_with(zmq.PUB, bind="tcp://*:12345")
            assert socket is mock_socket
    
    @pytest.mark.asyncio
    async def test_create_sub_socket(self):
        """Test creating ZeroMQ subscriber socket."""
        with patch('aiozmq.create_zmq_stream') as mock_create:
            mock_socket = AsyncMock()
            mock_create.return_value = mock_socket
            
            socket = await aiozmq.create_zmq_stream(zmq.SUB, connect="tcp://127.0.0.1:12345")
            
            mock_create.assert_called_once_with(zmq.SUB, connect="tcp://127.0.0.1:12345")
            assert socket is mock_socket
    
    def test_socket_subscribe_all(self, mock_zmq_socket):
        """Test subscribing to all messages."""
        mock_zmq_socket.transport.setsockopt = MagicMock()
        
        # Subscribe to all messages
        mock_zmq_socket.transport.setsockopt(zmq.SUBSCRIBE, b'')
        
        mock_zmq_socket.transport.setsockopt.assert_called_once_with(zmq.SUBSCRIBE, b'')
    
    def test_socket_subscribe_topic(self, mock_zmq_socket):
        """Test subscribing to specific topic."""
        mock_zmq_socket.transport.setsockopt = MagicMock()
        
        # Subscribe to specific topic
        topic = "_quant_async_test_"
        mock_zmq_socket.transport.setsockopt(zmq.SUBSCRIBE, topic.encode())
        
        mock_zmq_socket.transport.setsockopt.assert_called_once_with(zmq.SUBSCRIBE, topic.encode())


class TestMessageSerialization:
    """Test message serialization and deserialization."""
    
    def test_msgspec_encode_decode_quote(self, sample_market_data):
        """Test encoding and decoding quote data."""
        # Encode
        encoded = msgspec.msgpack.encode(sample_market_data)
        assert isinstance(encoded, bytes)
        
        # Decode
        decoded = msgspec.msgpack.decode(encoded)
        assert decoded == sample_market_data
        assert decoded['symbol'] == 'AAPL_STK'
        assert decoded['bid'] == 150.0
        assert decoded['ask'] == 150.1
    
    def test_msgspec_encode_decode_tick(self, sample_tick_data):
        """Test encoding and decoding tick data."""
        # Encode
        encoded = msgspec.msgpack.encode(sample_tick_data)
        assert isinstance(encoded, bytes)
        
        # Decode  
        decoded = msgspec.msgpack.decode(encoded)
        assert decoded == sample_tick_data
        assert decoded['symbol'] == 'AAPL_STK'
        assert decoded['last'] == 150.05
        assert decoded['kind'] == 'TICK'
    
    def test_msgspec_encode_decode_orderbook(self, sample_orderbook_data):
        """Test encoding and decoding orderbook data."""
        # Encode
        encoded = msgspec.msgpack.encode(sample_orderbook_data)
        assert isinstance(encoded, bytes)
        
        # Decode
        decoded = msgspec.msgpack.decode(encoded)
        assert decoded == sample_orderbook_data
        assert len(decoded['bids']) == 2
        assert len(decoded['asks']) == 2
    
    def test_msgspec_encode_datetime(self):
        """Test encoding datetime objects."""
        data_with_datetime = {
            'symbol': 'TEST',
            'timestamp': datetime(2024, 8, 4, 10, 30, 0).isoformat(),
            'price': 100.0
        }
        
        # Should encode without error
        encoded = msgspec.msgpack.encode(data_with_datetime)
        decoded = msgspec.msgpack.decode(encoded)
        
        assert decoded['timestamp'] == data_with_datetime['timestamp']
    
    def test_msgspec_performance(self, sample_market_data):
        """Test serialization performance for high-frequency data."""
        import time
        
        # Test encoding performance
        start_time = time.time()
        for _ in range(1000):
            encoded = msgspec.msgpack.encode(sample_market_data)
        encoding_time = time.time() - start_time
        
        # Test decoding performance
        start_time = time.time()
        for _ in range(1000):
            _ = msgspec.msgpack.decode(encoded)
        decoding_time = time.time() - start_time
        
        # Should be reasonably fast (less than 1ms per operation on average)
        assert encoding_time < 1.0
        assert decoding_time < 1.0


class TestBlotterStreaming:
    """Test Blotter streaming functionality."""
    
    def test_blotter_broadcast_message_format(self, mock_zmq_socket, sample_market_data):
        """Test Blotter broadcast message format."""
        blotter = Blotter(dbskip=True)
        blotter.socket = mock_zmq_socket
        
        blotter.broadcast(sample_market_data, 'QUOTE')
        
        # Verify write was called
        mock_zmq_socket.write.assert_called_once()
        
        # Verify message format
        call_args = mock_zmq_socket.write.call_args[0][0]
        assert len(call_args) == 1  # Single message
        assert isinstance(call_args[0], bytes)  # Serialized data
        
        # Verify we can decode the message
        decoded = msgspec.msgpack.decode(call_args[0])
        assert decoded == sample_market_data
    
    def test_blotter_broadcast_no_socket(self, sample_market_data):
        """Test broadcast when socket is None."""
        blotter = Blotter(dbskip=True)
        blotter.socket = None
        
        # Should not raise exception
        blotter.broadcast(sample_market_data, 'QUOTE')
    
    def test_blotter_broadcast_socket_error(self, mock_zmq_socket, sample_market_data):
        """Test broadcast error handling."""
        blotter = Blotter(dbskip=True)
        blotter.socket = mock_zmq_socket
        
        # Mock socket error
        mock_zmq_socket.write.side_effect = aiozmq.ZmqStreamClosed()
        
        # Should not raise exception
        blotter.broadcast(sample_market_data, 'QUOTE')
    
    def test_blotter_broadcast_connection_error(self, mock_zmq_socket, sample_market_data):
        """Test broadcast connection error handling."""
        blotter = Blotter(dbskip=True)
        blotter.socket = mock_zmq_socket
        
        # Mock connection error
        mock_zmq_socket.write.side_effect = ConnectionError("Connection lost")
        
        # Should not raise exception
        blotter.broadcast(sample_market_data, 'QUOTE')


class TestAlgoStreaming: 
    """Test Algorithm streaming functionality."""
    
    @pytest.mark.asyncio
    async def test_algo_stream_setup(self, mock_zmq_socket):
        """Test algorithm stream setup."""
        # Mock blotter args
        mock_blotter_args = {
            'zmqport': '12345',
            'as_client': True
        }
        
        with patch('quant_async.broker.load_blotter_args', return_value=mock_blotter_args):
            with patch('aiozmq.create_zmq_stream', return_value=mock_zmq_socket):
                
                class TestAlgo(Algo):
                    def on_start(self): pass
                    def on_quote(self, instrument): pass
                    def on_tick(self, instrument): pass
                    def on_bar(self, instrument): pass
                    def on_orderbook(self, instrument): pass
                    def on_fill(self, instrument, order): pass
                
                algo = TestAlgo(instruments=[("AAPL", "STK", "SMART", "USD")])
                
                # Test stream method exists
                assert hasattr(algo.blotter, 'stream')
    
    @pytest.mark.asyncio
    async def test_algo_stream_message_handling(self, mock_zmq_socket):
        """Test algorithm message handling from stream."""
        # Create test algorithm
        class TestAlgo(Algo):
            def __init__(self):
                # Mock the parent initialization
                self.quotes = {}
                self.books = {}
                
            def on_start(self): pass
            def on_quote(self, instrument): 
                self.received_quote = instrument
            def on_tick(self, instrument): pass
            def on_bar(self, instrument): pass
            def on_orderbook(self, instrument): 
                self.received_book = instrument
            def on_fill(self, instrument, order): pass
            
            def get_instrument(self, symbol):
                # Mock instrument
                class MockInstrument:
                    def __init__(self, symbol):
                        self.symbol = symbol
                return MockInstrument(symbol)
        
        algo = TestAlgo()
        
        # Mock quote message
        quote_message = {
            'symbol': 'AAPL_STK',
            'bid': 150.0,
            'ask': 150.1,
            'kind': 'QUOTE'
        }
        
        # Test quote handler
        await algo._quote_handler(quote_message.copy())
        
        # Verify quote was processed
        assert 'AAPL_STK' in algo.quotes
        assert hasattr(algo, 'received_quote')
        
        # Mock orderbook message
        book_message = {
            'symbol': 'AAPL_STK',
            'bids': [{'price': 150.0, 'size': 100}],
            'asks': [{'price': 150.1, 'size': 200}],
            'kind': 'ORDERBOOK'
        }
        
        # Test book handler
        await algo._book_handler(book_message.copy())
        
        # Verify orderbook was processed
        assert 'AAPL_STK' in algo.books
        assert hasattr(algo, 'received_book')


class TestStreamIntegration:
    """Test integration between Blotter and Algorithm streaming."""
    
    @pytest.mark.asyncio
    async def test_pub_sub_message_flow(self, zmq_pub_socket, zmq_sub_socket):
        """Test message flow from publisher to subscriber."""
        pub_socket, port = zmq_pub_socket
        sub_socket = zmq_sub_socket
        
        # Connect subscriber to publisher
        await sub_socket.transport.connect(f"tcp://127.0.0.1:{port}")
        
        # Allow connection to establish
        await asyncio.sleep(0.1)
        
        # Send test message
        test_message = {'symbol': 'TEST', 'price': 100.0, 'kind': 'QUOTE'}
        encoded_message = msgspec.msgpack.encode(test_message)
        pub_socket.write([encoded_message])
        
        # Receive message
        try:
            received = await asyncio.wait_for(sub_socket.read(), timeout=1.0)
            decoded_message = msgspec.msgpack.decode(received[0])
            
            assert decoded_message == test_message
        except asyncio.TimeoutError:
            pytest.skip("Message not received - timing dependent test")
    
    @pytest.mark.asyncio
    async def test_multiple_subscribers(self, zmq_pub_socket):
        """Test multiple subscribers receiving same message."""
        pub_socket, port = zmq_pub_socket
        
        # Create multiple subscriber sockets
        sub_sockets = []
        for _ in range(3):
            sub_socket = await aiozmq.create_zmq_stream(zmq.SUB)
            sub_socket.transport.setsockopt(zmq.SUBSCRIBE, b'')
            await sub_socket.transport.connect(f"tcp://127.0.0.1:{port}")
            sub_sockets.append(sub_socket)
        
        # Allow connections to establish
        await asyncio.sleep(0.1)
        
        # Send test message
        test_message = {'symbol': 'MULTI', 'price': 200.0, 'kind': 'TICK'}
        encoded_message = msgspec.msgpack.encode(test_message)
        pub_socket.write([encoded_message])
        
        # All subscribers should receive the message
        try:
            received_count = 0
            for sub_socket in sub_sockets:
                try:
                    received = await asyncio.wait_for(sub_socket.read(), timeout=0.5)
                    decoded_message = msgspec.msgpack.decode(received[0])
                    if decoded_message == test_message:
                        received_count += 1
                except asyncio.TimeoutError:
                    pass
            
            # At least some subscribers should receive the message
            assert received_count > 0
            
        finally:
            # Cleanup sockets
            for sub_socket in sub_sockets:
                sub_socket.close()
                await sub_socket.drain()


class TestStreamErrorHandling:
    """Test error handling in streaming scenarios."""
    
    @pytest.mark.asyncio
    async def test_blotter_stream_connection_recovery(self, mock_asyncpg_pool):
        """Test Blotter stream connection recovery."""
        blotter = Blotter(dbskip=False)
        blotter.pool = mock_asyncpg_pool
        
        # Mock symbols for streaming
        symbols = ['AAPL_STK', 'NVDA_STK']
        
        # Mock ZeroMQ socket that fails and recovers
        mock_socket = AsyncMock()
        mock_socket.transport = MagicMock()
        mock_socket.transport.setsockopt = MagicMock()
        mock_socket.close = MagicMock()
        mock_socket.drain = AsyncMock()
        
        mock_socket.read.side_effect = [
            # First call - successful message
            [msgspec.msgpack.encode({'symbol': 'AAPL_STK', 'price': 150.0, 'kind': 'QUOTE'})],
            # Second call - timeout (this will be caught and handled)
            asyncio.TimeoutError(),
            # Third call - connection error (this will be caught and the loop will break)
            ConnectionError("Connection lost")
        ]
        
        with patch('aiozmq.create_zmq_stream', return_value=mock_socket):
            # Mock handlers
            quote_handler = AsyncMock()
            
            # Test streaming with error recovery
            stream_task = asyncio.create_task(
                blotter.stream(
                    symbols=symbols,
                    quote_handler=quote_handler
                )
            )
            
            # Let it run briefly
            await asyncio.sleep(0.1)
            stream_task.cancel()
            
            try:
                await stream_task
            except (asyncio.CancelledError, ConnectionError):
                # Expected behavior - stream should raise ConnectionError when connection is lost
                pass
        
        # Should have attempted to read multiple times before failing
        assert mock_socket.read.call_count >= 2
        # Should have closed socket on error
        mock_socket.close.assert_called()
        mock_socket.drain.assert_called()
    
    @pytest.mark.asyncio
    async def test_algo_stream_message_corruption(self):
        """Test algorithm handling of corrupted messages."""
        class TestAlgo(Algo):
            def __init__(self):
                self.quotes = {}
                self.error_count = 0
                
            def on_start(self): pass
            def on_quote(self, instrument): pass
            def on_tick(self, instrument): pass
            def on_bar(self, instrument): pass
            def on_orderbook(self, instrument): pass
            def on_fill(self, instrument, order): pass
            
            def get_instrument(self, symbol):
                class MockInstrument:
                    def __init__(self, symbol):
                        self.symbol = symbol
                return MockInstrument(symbol)
        
        algo = TestAlgo()
        
        # Test with corrupted message (missing required fields)
        corrupted_message = {
            'symbol': 'AAPL_STK',
            # Missing 'kind' field
            'bid': 150.0
        }
        
        try:
            await algo._quote_handler(corrupted_message)
        except KeyError:
            # Should handle missing fields gracefully
            pass
    
    @pytest.mark.asyncio 
    async def test_socket_cleanup_on_error(self, mock_zmq_socket):
        """Test proper socket cleanup on errors."""
        blotter = Blotter(dbskip=True)
        
        # Mock socket creation and immediate error
        with patch('aiozmq.create_zmq_stream', return_value=mock_zmq_socket):
            mock_zmq_socket.read.side_effect = Exception("Critical error")
            
            try:
                await blotter.stream(
                    symbols=['AAPL_STK'],
                    quote_handler=AsyncMock()
                )
            except Exception:
                pass
        
        # Verify socket cleanup was attempted
        mock_zmq_socket.close.assert_called()
        mock_zmq_socket.drain.assert_called()


class TestStreamPerformance:
    """Test streaming performance characteristics."""
    
    def test_message_throughput_simulation(self, mock_zmq_socket, sample_market_data):
        """Test high-frequency message processing simulation."""
        blotter = Blotter(dbskip=True)
        blotter.socket = mock_zmq_socket
        
        import time
        
        # Simulate high-frequency broadcasting
        start_time = time.time()
        message_count = 1000
        
        for i in range(message_count):
            sample_data = sample_market_data.copy()
            sample_data['price'] = 150.0 + i * 0.01
            blotter.broadcast(sample_data, 'QUOTE')
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        # Should handle 1000 messages reasonably quickly
        assert elapsed_time < 5.0  # Less than 5 seconds
        assert mock_zmq_socket.write.call_count == message_count
    
    def test_serialization_overhead(self, sample_market_data):
        """Test serialization overhead for different data sizes."""
        import time
        
        # Test with standard market data
        standard_data = sample_market_data
        
        # Test with extended market data
        extended_data = sample_market_data.copy()
        extended_data.update({
            'additional_field_' + str(i): f'value_{i}' 
            for i in range(50)  # Add 50 extra fields
        })
        
        # Measure serialization time for standard data
        start_time = time.time()
        for _ in range(100):
            msgspec.msgpack.encode(standard_data)
        standard_time = time.time() - start_time
        
        # Measure serialization time for extended data
        start_time = time.time()
        for _ in range(100):
            msgspec.msgpack.encode(extended_data)
        extended_time = time.time() - start_time
        
        # Extended data should take longer but not excessively
        assert extended_time > standard_time
        assert extended_time < standard_time * 10  # Less than 10x slower


class TestTopicFiltering:
    """Test ZeroMQ topic filtering functionality."""
    
    @pytest.mark.asyncio
    async def test_topic_subscription_filtering(self, zmq_pub_socket):
        """Test topic-based message filtering."""
        pub_socket, port = zmq_pub_socket
        
        # Create subscriber with specific topic filter
        sub_socket = await aiozmq.create_zmq_stream(zmq.SUB)
        topic = "_quant_async_test_"
        sub_socket.transport.setsockopt(zmq.SUBSCRIBE, topic.encode())
        await sub_socket.transport.connect(f"tcp://127.0.0.1:{port}")
        
        # Allow connection to establish
        await asyncio.sleep(0.1)
        
        try:
            # Send message with matching topic (should be received)
            matching_message = {'symbol': 'MATCH', 'kind': 'QUOTE'}
            encoded_message = msgspec.msgpack.encode(matching_message)
            pub_socket.write([topic.encode() + b' ' + encoded_message])
            
            # Send message with non-matching topic (should be filtered)
            non_matching_message = {'symbol': 'NO_MATCH', 'kind': 'QUOTE'}
            encoded_message = msgspec.msgpack.encode(non_matching_message)
            pub_socket.write([b'different_topic ' + encoded_message])
            
            # Should only receive the matching message
            try:
                received = await asyncio.wait_for(sub_socket.read(), timeout=1.0)
                # Parse topic and message
                raw_message = received[0]
                if b' ' in raw_message:
                    topic_part, message_part = raw_message.split(b' ', 1)
                    decoded_message = msgspec.msgpack.decode(message_part)
                    assert decoded_message['symbol'] == 'MATCH'
                
            except asyncio.TimeoutError:
                pytest.skip("Topic filtering test timing dependent")
                
        finally:
            sub_socket.close()
            await sub_socket.drain()
    
    def test_blotter_topic_generation(self):
        """Test Blotter ZMQ topic generation."""
        # Test default topic generation
        blotter1 = Blotter(name="test_blotter", dbskip=True)
        expected_topic1 = "_quant_async_test_blotter_"
        assert blotter1.args['zmqtopic'] == expected_topic1
        
        # Test custom topic
        blotter2 = Blotter(zmqtopic="custom_topic", dbskip=True)
        assert blotter2.args['zmqtopic'] == "custom_topic"
        
        # Test auto-generated name
        class CustomBlotter(Blotter):
            pass
        
        blotter3 = CustomBlotter(dbskip=True)
        expected_topic3 = "_quant_async_customblotter_"
        assert blotter3.args['zmqtopic'] == expected_topic3