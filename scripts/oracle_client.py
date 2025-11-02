#!/usr/bin/env python3
"""
GenLayer Oracle Client - Python

Off-chain Python script to interact with GenLayer oracle contracts.
Similar to src/index.ts but using genlayer-py SDK.

Usage:
    python scripts/oracle_client.py [contract_address]

Examples:
    # Read from deployed contract
    python scripts/oracle_client.py 0xe0E45EC84BB780BB1cccAc1B0CB09E507eF37147
    
    # Simple Price Feed
    python scripts/oracle_client.py 0xe328378CAF086ae0a6458395C9919a4137fCb888
"""

import sys
from typing import Optional

try:
    from genlayer_py import create_client, create_account, studionet
    from genlayer_py.types import Address
except ImportError:
    print("❌ Error: genlayer-py not installed")
    print("   Install with: pip install genlayer-py")
    sys.exit(1)


def read_simple_price_feed(client, address: Address) -> None:
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
    except Exception as e:
        print(f"❌ Error reading contract: {e}")
        print("\nNote: Make sure the contract is deployed and address is correct.")


def read_oracle_consumer(client, address: Address) -> None:
    """Read from Oracle Consumer contract."""
    print("\n--- Reading Oracle Consumer ---")
    
    try:
        status = client.read_contract(
            address=address,
            function_name="get_status",
            args=[],
        )
        
        print("\nOracle Status:")
        print(f"  Price: ${status.get('price', {}).get('eth_usd', 'N/A')} ({status.get('price', {}).get('source', 'N/A')})")
        
        weather = status.get('weather', {})
        print(f"  Weather: {weather.get('temperature', 'N/A')}°C, {weather.get('condition', 'N/A')} ({weather.get('city', 'N/A')})")
        
        news = status.get('news', {})
        print(f"  News Items: {news.get('count', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Error reading contract: {e}")
        print("\nNote: Make sure the contract is deployed and address is correct.")


def detect_contract_type(client, address: Address) -> Optional[str]:
    """Detect contract type by trying to read different methods."""
    # Try Oracle Consumer first (has get_status)
    try:
        client.read_contract(
            address=address,
            function_name="get_status",
            args=[],
        )
        return "oracle"
    except:
        pass
    
    # Try Simple Price Feed (has get_price)
    try:
        client.read_contract(
            address=address,
            function_name="get_price",
            args=[],
        )
        return "simple"
    except:
        pass
    
    return None


def main():
    """Main function."""
    contract_address: Optional[str] = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Create account and client
    account = create_account()
    client = create_client(chain=studionet, account=account)
    
    print("\n=== GenLayer Oracle Client (Python) ===")
    print(f"Chain: {studionet.name}")
    print(f"Account: {account.address}")
    
    if contract_address:
        print(f"\nContract Address: {contract_address}")
        
        # Detect contract type and read accordingly
        contract_type = detect_contract_type(client, contract_address)
        
        if contract_type == "oracle":
            read_oracle_consumer(client, contract_address)
        elif contract_type == "simple":
            read_simple_price_feed(client, contract_address)
        else:
            print("❌ Could not detect contract type.")
            print("   Make sure the contract address is correct and contract is deployed.")
    else:
        print("\n--- Usage ---")
        print("Provide contract address to read from contract:")
        print("  python scripts/oracle_client.py <contract_address>")
        print("\nExamples:")
        print("  python scripts/oracle_client.py 0xe0E45EC84BB780BB1cccAc1B0CB09E507eF37147  # Oracle Consumer")
        print("  python scripts/oracle_client.py 0xe328378CAF086ae0a6458395C9919a4137fCb888  # Simple Price Feed")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

