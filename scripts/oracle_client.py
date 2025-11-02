#!/usr/bin/env python3
# Note: This script requires Python 3.12+ (genlayer-py requirement)
# On Windows, recommended: py -3.12 scripts/oracle_client.py
# Python 3.14 may have dependency build issues (ckzg needs Visual Studio Build Tools)
"""
GenLayer Oracle Client - Python

Off-chain Python script to interact with GenLayer oracle contracts.
Similar to src/index.ts but using genlayer-py SDK.

IMPORTANT: Requires Python >=3.12 (genlayer-py SDK requirement)
If using Python <3.12, use TypeScript client instead: npm run dev

Usage:
    python scripts/oracle_client.py [contract_address] [action]

Actions:
    read    - Read from contract (default)
    update  - Update contract (write transaction)

Examples:
    # Read from deployed contract
    python scripts/oracle_client.py 0xe0E45EC84BB780BB1cccAc1B0CB09E507eF37147
    
    # Read Simple Price Feed
    python scripts/oracle_client.py 0xe328378CAF086ae0a6458395C9919a4137fCb888
    
    # Update Simple Price Feed
    python scripts/oracle_client.py 0xe328378CAF086ae0a6458395C9919a4137fCb888 update
"""

import sys
from typing import Optional

# ============================================================================
# GenLayer Python SDK Imports
# ============================================================================
# Note: This script uses genlayer-py (off-chain SDK)
#       Contracts use genlayer.gl (on-chain runtime)
#
# genlayer-py: For interacting with contracts from off-chain Python scripts
# genlayer.gl: For writing contracts that run on GenVM (on-chain)
# ============================================================================

try:
    from genlayer_py import create_client, create_account
    from genlayer_py.types import TransactionStatus
except ImportError as e:
    print("ERROR: genlayer-py not installed or incompatible")
    print("   Install with: pip install genlayer-py")
    print("   Note: genlayer-py requires Python >= 3.12")
    print(f"   Current Python: {sys.version}")
    print(f"   Import error: {e}")
    sys.exit(1)

# Try to import studionet, fallback to localnet if not available
try:
    from genlayer_py.chains import studionet
    CHAIN = studionet
except ImportError:
    try:
        from genlayer_py.chains import localnet
        CHAIN = localnet
        print("WARNING: studionet not found, using localnet")
        print("   If you need studionet, check genlayer-py version or create custom config")
    except ImportError:
        print("ERROR: Could not import chain configuration")
        sys.exit(1)


def read_simple_price_feed(client, address: str) -> None:
    """Read from Simple Price Feed contract."""
    print("\n--- Reading Simple Price Feed ---")
    
    try:
        result = client.read_contract(
            address=address,
            function_name="get_price",
            args=[],
        )
        
        print(f"Price: ${result.get('price', 'N/A')}")
        print(f"Source: {result.get('source', 'N/A')}")
        return result
    except Exception as e:
        print(f"ERROR: Error reading contract: {e}")
        print("\nNote: Make sure the contract is deployed and address is correct.")
        return None


def read_oracle_consumer(client, address: str) -> None:
    """Read from Oracle Consumer contract."""
    print("\n--- Reading Oracle Consumer ---")
    
    try:
        status = client.read_contract(
            address=address,
            function_name="get_status",
            args=[],
        )
        
        print("\nOracle Status:")
        price_info = status.get('price', {})
        print(f"  Price: ${price_info.get('eth_usd', 'N/A')} ({price_info.get('source', 'N/A')})")
        
        weather = status.get('weather', {})
        print(f"  Weather: {weather.get('temperature', 'N/A')}°C, {weather.get('condition', 'N/A')} ({weather.get('city', 'N/A')})")
        
        news = status.get('news', {})
        print(f"  News Items: {news.get('count', 'N/A')}")
        
        return status
    except Exception as e:
        print(f"ERROR: Error reading contract: {e}")
        print("\nNote: Make sure the contract is deployed and address is correct.")
        return None


def update_simple_price_feed(client, account, address: str) -> None:
    """Update Simple Price Feed contract."""
    print("\n--- Updating Simple Price Feed ---")
    
    try:
        print("Sending update_price transaction...")
        tx_hash = client.write_contract(
            account=account,
            address=address,
            function_name="update_price",
            args=[],
            value=0,
        )
        
        print(f"SUCCESS: Transaction sent: {tx_hash}")
        print("Waiting for finalization...")
        
        receipt = client.wait_for_transaction_receipt(
            hash=tx_hash,
            status=TransactionStatus.FINALIZED,
            full_transaction=False,
        )
        
        print(f"SUCCESS: Transaction finalized!")
        
        # Read updated price
        print("\nReading updated price...")
        read_simple_price_feed(client, address)
        
    except Exception as e:
        print(f"ERROR: Error updating contract: {e}")
        import traceback
        traceback.print_exc()


def update_oracle_consumer(client, account, address: str) -> None:
    """Update Oracle Consumer contract."""
    print("\n--- Updating Oracle Consumer ---")
    
    try:
        print("Sending update_all transaction...")
        tx_hash = client.write_contract(
            account=account,
            address=address,
            function_name="update_all",
            args=["Hanoi", "21.0245", "105.8412", 3],
            value=0,
        )
        
        print(f"SUCCESS: Transaction sent: {tx_hash}")
        print("Waiting for finalization...")
        
        receipt = client.wait_for_transaction_receipt(
            hash=tx_hash,
            status=TransactionStatus.FINALIZED,
            full_transaction=False,
        )
        
        print(f"SUCCESS: Transaction finalized!")
        
        # Read updated status
        print("\nReading updated status...")
        read_oracle_consumer(client, address)
        
    except Exception as e:
        print(f"ERROR: Error updating contract: {e}")
        import traceback
        traceback.print_exc()


def detect_contract_type(client, address: str) -> Optional[str]:
    """Detect contract type by trying to read different methods."""
    # Try Oracle Consumer first (has get_status)
    try:
        client.read_contract(
            address=address,
            function_name="get_status",
            args=[],
        )
        return "oracle"
    except Exception as e:
        # If error, try next method
        pass
    
    # Try Simple Price Feed (has get_price)
    try:
        client.read_contract(
            address=address,
            function_name="get_price",
            args=[],
        )
        return "simple"
    except Exception as e:
        # If both fail, return None
        pass
    
    return None


def main():
    """Main function."""
    contract_address: Optional[str] = sys.argv[1] if len(sys.argv) > 1 else None
    action: str = sys.argv[2] if len(sys.argv) > 2 else "read"
    
    # Create account and client
    account = create_account()
    # Note: genlayer-py requires account in create_client for read_contract
    client = create_client(chain=CHAIN, account=account)
    
    print("\n=== GenLayer Oracle Client (Python) ===")
    print(f"Chain: {CHAIN.name if hasattr(CHAIN, 'name') else 'Unknown'}")
    print(f"Account: {account.address}")
    
    if contract_address:
        print(f"\nContract Address: {contract_address}")
        print(f"Action: {action}")
        
        # Detect contract type
        contract_type = detect_contract_type(client, contract_address)
        
        if contract_type is None:
            print("ERROR: Could not detect contract type.")
            print("   Make sure the contract address is correct and contract is deployed.")
            return
        
        # Execute action
        if action == "read":
            if contract_type == "oracle":
                read_oracle_consumer(client, contract_address)
            elif contract_type == "simple":
                read_simple_price_feed(client, contract_address)
        elif action == "update":
            if contract_type == "oracle":
                update_oracle_consumer(client, account, contract_address)
            elif contract_type == "simple":
                update_simple_price_feed(client, account, contract_address)
        else:
            print(f"ERROR: Unknown action: {action}")
            print("   Available actions: read, update")
    else:
        print("\n--- Usage ---")
        print("Provide contract address to interact with contract:")
        print("  python scripts/oracle_client.py <contract_address> [action]")
        print("\nActions:")
        print("  read    - Read from contract (default)")
        print("  update  - Update contract (write transaction)")
        print("\nExamples:")
        print("  # Read from Oracle Consumer")
        print("  python scripts/oracle_client.py 0xe0E45EC84BB780BB1cccAc1B0CB09E507eF37147")
        print("\n  # Read from Simple Price Feed")
        print("  python scripts/oracle_client.py 0xe328378CAF086ae0a6458395C9919a4137fCb888")
        print("\n  # Update Simple Price Feed")
        print("  python scripts/oracle_client.py 0xe328378CAF086ae0a6458395C9919a4137fCb888 update")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
