# tests/test_flow.py

import pytest
from prefect import flow
from orchestrator.flow import fluxpilot_flow

def test_flow_runs():
    # Simply ensure the flow can be called without exceptions
    result = fluxpilot_flow()
    assert result is None  # flow returns None on success
