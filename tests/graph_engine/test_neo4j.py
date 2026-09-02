import pytest
from unittest.mock import patch, MagicMock
from services.graph_engine.neo4j_driver import GraphEngine

def test_neo4j_connection_failure():
    # Test that invalid credentials or offline DB doesn't crash the app but logs the error
    with patch('services.graph_engine.neo4j_driver.GraphDatabase.driver', side_effect=Exception("Connection Refused")):
        engine = GraphEngine(uri="bolt://invalid:7687")
        assert engine.driver is None

def test_create_actor_cluster():
    with patch('services.graph_engine.neo4j_driver.GraphDatabase.driver') as mock_driver:
        # Set up the mock chain: driver.session().run().single()
        mock_session = MagicMock()
        mock_driver.return_value.session.return_value.__enter__.return_value = mock_session
        
        mock_result = MagicMock()
        mock_result.single.return_value = {"a": {"id": "ACTOR-123", "confidence": 0.9}}
        mock_session.run.return_value = mock_result
        
        engine = GraphEngine()
        result = engine.create_actor_cluster("ACTOR-123", 0.9, 0.8)
        
        # Verify the query was executed with correct parameters
        assert mock_session.run.called
        args, kwargs = mock_session.run.call_args
        assert "MERGE (a:ActorCluster" in args[0]
        assert kwargs["cluster_id"] == "ACTOR-123"
        assert kwargs["confidence"] == 0.9
        assert result == {"a": {"id": "ACTOR-123", "confidence": 0.9}}

def test_link_wallets_malformed():
    with patch('services.graph_engine.neo4j_driver.GraphDatabase.driver') as mock_driver:
        mock_session = MagicMock()
        mock_driver.return_value.session.return_value.__enter__.return_value = mock_session
        
        engine = GraphEngine()
        
        # Test missing transaction hash behavior (e.g. None). Neo4j might fail if we pass None to a property.
        # But our driver just passes the param directly. Let's ensure it calls run with the param.
        engine.link_wallets("1A1zP1", "1BvBMSE", None)
        args, kwargs = mock_session.run.call_args
        assert kwargs["tx_hash"] is None
