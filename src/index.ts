import { createClient, createAccount, Address } from "genlayer-js";
import { studionet } from "genlayer-js/chains";

/**
 * GenLayer Oracle Demo
 * 
 * This script demonstrates:
 * 1. Off-chain API clients (for testing without contract)
 * 2. Contract interaction (when contract address is provided)
 * 
 * Usage:
 *   node dist/index.js [contractAddress]
 * 
 * Example:
 *   node dist/index.js 0xe406bdB51798A5EE0a8920f813E8579664d35445
 */
async function main() {
  const contractAddress = process.argv[2] as Address | undefined;
  const account = createAccount();
  const client = createClient({ chain: studionet, account });
  
  console.log(`\n=== GenLayer Oracle Demo ===`);
  console.log(`Chain: ${studionet.name}`);
  console.log(`Account: ${account.address}`);
  
  if (contractAddress) {
    console.log(`\nContract Address: ${contractAddress}`);
    console.log('\n--- Reading from Contract ---');
    
    try {
      const status = await client.readContract({
        address: contractAddress,
        functionName: 'get_status',
        args: [],
      });
      
      console.log('Oracle Status:', JSON.stringify(status, null, 2));
    } catch (e: any) {
      console.error('Error reading contract:', e.message);
      console.log('\nNote: Make sure the contract is deployed and address is correct.');
    }
  } else {
    console.log('\n--- Off-chain API Demo ---');
    console.log('(No contract address provided - using API clients directly)');
    console.log('\nTo use contract, run: node dist/index.js <contractAddress>');
    
    // Off-chain API demo (for testing without contract)
    const { priceClient, openMeteoClient, newsClient } = await import("genlayer-js/api");
    
    try {
      const eth = await priceClient.getPrice('ETH');
      console.log(`\nETH Price: $${eth.price} (${eth.source})`);

      const weather = await openMeteoClient.getCurrent(21.0245, 105.8412, 'Hanoi');
      console.log(`Weather: ${weather.temperature}°C, ${weather.condition}`);

      const news = await newsClient.getCryptoNews(3);
      console.log(`News Items: ${news.length}`);
    } catch (e: any) {
      console.error('Error fetching data:', e.message);
    }
  }
}

main().catch(console.error);



