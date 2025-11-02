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

```typescript
import { OracleSDK } from '@genlayer/oracle-sdk';
import { createClient, createAccount } from 'genlayer-js';
import { studionet } from 'genlayer-js/chains';

// Setup
const account = createAccount();
const client = createClient({ chain: studionet, account });

// Create Oracle SDK instance
const oracle = new OracleSDK({
  contractAddress: '0x...',
  chain: studionet,
  client: client
});

// Get current status
const status = await oracle.getStatus();
console.log('ETH Price:', status.price.eth_usd);

// Subscribe to updates
oracle.onUpdate((data) => {
  console.log('Oracle updated:', data);
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
- `getNews(): Promise<NewsData>` - Get news count
- `updateOracle(params?: UpdateParams): Promise<string>` - Trigger oracle update (returns tx hash)
- `onUpdate(callback: (data: OracleStatus) => void): void` - Subscribe to updates
- `offUpdate(callback: Function): void` - Unsubscribe from updates

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

### Multi-oracle Aggregation

```typescript
import { MultiOracleSDK } from '@genlayer/oracle-sdk';

const multiOracle = new MultiOracleSDK({
  oracles: [
    { address: '0x...', chain: studionet },
    { address: '0x...', chain: studionet },
  ],
  client: client
});

// Get average price from all oracles
const avgPrice = await multiOracle.getAveragePrice('ETH');
```

## License

MIT

