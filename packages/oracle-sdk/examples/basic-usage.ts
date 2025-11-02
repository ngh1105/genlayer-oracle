/**
 * Basic Usage Example - Oracle SDK
 * 
 * Demonstrates how to use the Oracle SDK to interact with deployed contracts
 */
import { createClient, createAccount } from 'genlayer-js';
import { studionet } from 'genlayer-js/chains';
import { OracleSDK, SimplePriceFeedSDK } from '../src/index';

// Deployed contract addresses
const ORACLE_CONSUMER_ADDRESS = '0xe0E45EC84BB780BB1cccAc1B0CB09E507eF37147';
const SIMPLE_PRICE_FEED_ADDRESS = '0xe328378CAF086ae0a6458395C9919a4137fCb888';

async function main() {
  // Setup client
  const account = createAccount();
  const client = createClient({ chain: studionet, account });

  console.log('=== Oracle SDK Examples ===\n');

  // Example 1: Simple Price Feed
  console.log('--- Example 1: Simple Price Feed ---');
  const simpleSDK = new SimplePriceFeedSDK({
    contractAddress: SIMPLE_PRICE_FEED_ADDRESS,
    chain: studionet,
    client,
  });

  try {
    const price = await simpleSDK.getPrice();
    console.log(`Current ETH Price: $${price.price} (${price.source})`);
    
    // Update price
    console.log('\nUpdating price...');
    const txHash = await simpleSDK.updatePrice();
    console.log(`Transaction: ${txHash}`);
    
    // Wait for finalization
    await simpleSDK.waitForFinalization(txHash);
    console.log('Transaction finalized!');
    
    // Get updated price
    const newPrice = await simpleSDK.getPrice();
    console.log(`Updated ETH Price: $${newPrice.price} (${newPrice.source})`);
  } catch (error: any) {
    console.error('Error:', error.message);
  }

  // Example 2: Oracle Consumer (Full Oracle)
  console.log('\n--- Example 2: Oracle Consumer ---');
  const oracleSDK = new OracleSDK({
    contractAddress: ORACLE_CONSUMER_ADDRESS,
    chain: studionet,
    client,
  });

  try {
    const status = await oracleSDK.getStatus();
    console.log('Oracle Status:');
    console.log(`  ETH Price: $${status.price.eth_usd} (${status.price.source})`);
    console.log(`  Weather: ${status.weather.temperature}°C in ${status.weather.city}`);
    console.log(`  News Count: ${status.news.count}`);

    // Subscribe to updates
    oracleSDK.onUpdate((data) => {
      console.log('\nOracle Updated!');
      console.log(`  New Price: $${data.price.eth_usd}`);
      console.log(`  New Weather: ${data.weather.temperature}°C`);
    });

    // Update oracle
    console.log('\nUpdating oracle...');
    const txHash = await oracleSDK.updateOracle({
      city: 'Hanoi',
      lat: '21.0245',
      lon: '105.8412',
      newsLimit: 3,
    });
    console.log(`Transaction: ${txHash}`);
    
    // Wait for finalization
    await oracleSDK.waitForFinalization(txHash);
    console.log('Transaction finalized!');

    // Cleanup
    setTimeout(() => {
      oracleSDK.destroy();
      simpleSDK.destroy();
      console.log('\nSDKs destroyed');
    }, 30000);
  } catch (error: any) {
    console.error('Error:', error.message);
  }
}

main().catch(console.error);

