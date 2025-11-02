# GenLayer Oracle SDK

TypeScript/JavaScript SDK for interacting with GenLayer oracle contracts. Provides type-safe, easy-to-use interface for querying oracle data and subscribing to updates.

## Features

- ✅ **Type-safe**: Full TypeScript support with autocomplete
- ✅ **Event subscriptions**: Listen to oracle updates in real-time
- ✅ **Multi-oracle support**: Aggregate data from multiple oracle contracts
- ✅ **Easy integration**: Simple API for common use cases
- ✅ **Error handling**: Built-in error handling and retries

## Installation

```bash
npm install @genlayer/oracle-sdk
# or
yarn add @genlayer/oracle-sdk
```

## Quick Start

### Oracle Consumer (Full Oracle)

```typescript
import { OracleSDK } from '@genlayer/oracle-sdk';
import { createClient, createAccount } from 'genlayer-js';
import { studionet } from 'genlayer-js/chains';

// Setup
const account = createAccount();
const client = createClient({ chain: studionet, account });

// Create Oracle SDK instance
const oracle = new OracleSDK({
  contractAddress: '0xe0E45EC84BB780BB1cccAc1B0CB09E507eF37147', // Deployed Oracle Consumer
  chain: studionet,
  client: client
});

// Get current status
const status = await oracle.getStatus();
console.log('ETH Price:', status.price.eth_usd);
console.log('Weather:', status.weather.temperature, '°C');
console.log('News:', status.news.count);

// Update oracle
const txHash = await oracle.updateOracle({ city: 'Hanoi' });
await oracle.waitForFinalization(txHash);

// Subscribe to updates
oracle.onUpdate((data) => {
  console.log('Oracle updated:', data);
});
```

### Simple Price Feed

```typescript
import { SimplePriceFeedSDK } from '@genlayer/oracle-sdk';
import { createClient, createAccount } from 'genlayer-js';
import { studionet } from 'genlayer-js/chains';

// Setup
const account = createAccount();
const client = createClient({ chain: studionet, account });

// Create Simple Price Feed SDK
const priceSDK = new SimplePriceFeedSDK({
  contractAddress: '0xe328378CAF086ae0a6458395C9919a4137fCb888', // Deployed Simple Price Feed
  chain: studionet,
  client: client
});

// Get current price
const price = await priceSDK.getPrice();
console.log(`ETH Price: $${price.price} (${price.source})`);

// Update price and wait
const newPrice = await priceSDK.updatePriceAndWait();
console.log(`Updated Price: $${newPrice.price}`);

// Subscribe to price updates
priceSDK.onUpdate((data) => {
  console.log(`Price updated: $${data.price}`);
});
```

## API Reference

### OracleSDK

Main SDK class for interacting with oracle contracts.

#### Constructor

```typescript
new OracleSDK(options: {
  contractAddress: Address;
  chain: GenLayerChain;
  client: GenLayerClient;
})
```

#### Methods

- `getStatus(): Promise<OracleStatus>` - Get current oracle status
- `getPrice(symbol?: string): Promise<number>` - Get price for symbol (default: ETH)
- `getWeather(): Promise<WeatherData>` - Get weather data
- `getNews(): Promise<number>` - Get news count
- `updateOracle(params?: UpdateParams): Promise<string>` - Trigger oracle update (returns tx hash)
- `waitForFinalization(txHash: string): Promise<any>` - Wait for transaction to finalize
- `onUpdate(callback: (data: OracleStatus) => void): void` - Subscribe to updates
- `offUpdate(callback: Function): void` - Unsubscribe from updates
- `destroy(): void` - Cleanup (stop polling)

### SimplePriceFeedSDK

SDK for Simple Price Feed contracts (price-only oracle).

#### Methods

- `getPrice(): Promise<SimplePriceData>` - Get current price
- `getPriceNumber(): Promise<number>` - Get price as number
- `updatePrice(): Promise<string>` - Trigger price update (returns tx hash)
- `updatePriceAndWait(): Promise<SimplePriceData>` - Update and wait for finalization
- `waitForFinalization(txHash: string): Promise<any>` - Wait for transaction
- `onUpdate(callback: (data: SimplePriceData) => void): void` - Subscribe to updates
- `offUpdate(callback: Function): void` - Unsubscribe
- `destroy(): void` - Cleanup

### OracleStatus

Type definition for oracle status:

```typescript
interface OracleStatus {
  price: {
    eth_usd: string;
    source: string;
  };
  weather: {
    temperature: string;
    condition: string;
    city: string;
  };
  news: {
    count: number;
  };
}
```

## Examples

### Basic Usage

```typescript
const oracle = new OracleSDK({
  contractAddress: '0x...',
  chain: studionet,
  client: client
});

const status = await oracle.getStatus();
console.log(status);
```

### Subscribe to Updates

```typescript
oracle.onUpdate((data) => {
  console.log('New price:', data.price.eth_usd);
  console.log('Source:', data.price.source);
  console.log('Weather:', data.weather.temperature);
});

// Later, unsubscribe
oracle.offUpdate(updateCallback);
```

### Trigger Update

```typescript
const txHash = await oracle.updateOracle({
  city: 'Hanoi',
  lat: '21.0245',
  lon: '105.8412',
  newsLimit: 5
});

console.log('Transaction:', txHash);

// Wait for finalization
const receipt = await client.waitForTransactionReceipt({
  hash: txHash,
  status: 'finalized'
});
```

### Error Handling

```typescript
try {
  const status = await oracle.getStatus();
} catch (error) {
  console.error('Failed to get status:', error.message);
  // Handle error (contract not deployed, network issue, etc.)
}
```

## Deployed Contracts

The SDK is tested with these deployed contracts on studionet:

- **Simple Price Feed**: `0xe328378CAF086ae0a6458395C9919a4137fCb888`
- **Oracle Consumer**: `0xe0E45EC84BB780BB1cccAc1B0CB09E507eF37147`

## License

MIT

