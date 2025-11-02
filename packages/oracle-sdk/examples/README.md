# Oracle SDK Examples

Examples demonstrating how to use the Oracle SDK with deployed contracts.

## Prerequisites

```bash
cd packages/oracle-sdk
npm install
```

## Examples

### Basic Usage (`basic-usage.ts`)

Demonstrates:
- Reading price from Simple Price Feed
- Updating price and waiting for finalization
- Reading full oracle status from Oracle Consumer
- Subscribing to updates
- Error handling

**Run**:
```bash
npx tsx examples/basic-usage.ts
```

## Deployed Contracts

These examples use the following deployed contracts on studionet:

- **Simple Price Feed**: `0xe328378CAF086ae0a6458395C9919a4137fCb888`
- **Oracle Consumer**: `0xe0E45EC84BB780BB1cccAc1B0CB09E507eF37147`

## Usage Tips

1. **Wait for Finalization**: Always wait for transactions to finalize before reading state
2. **Polling Interval**: SDK uses 5s polling by default (can be customized)
3. **Cleanup**: Call `destroy()` to stop polling when done
4. **Error Handling**: All methods throw errors that should be caught

