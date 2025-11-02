/**
 * Simple Price Feed SDK
 * 
 * TypeScript SDK for interacting with Simple Price Feed contracts
 */
import type { GenLayerClient, GenLayerChain, Address } from './OracleSDK';

export interface SimplePriceData {
  price: string;
  source: string;
}

export interface SimplePriceFeedSDKOptions {
  contractAddress: Address;
  chain: GenLayerChain;
  client: GenLayerClient<GenLayerChain>;
}

export class SimplePriceFeedSDK {
  private contractAddress: Address;
  private chain: GenLayerChain;
  private client: GenLayerClient<GenLayerChain>;
  private updateCallbacks: Set<(data: SimplePriceData) => void> = new Set();
  private pollingInterval?: NodeJS.Timeout;

  constructor(options: SimplePriceFeedSDKOptions) {
    this.contractAddress = options.contractAddress;
    this.chain = options.chain;
    this.client = options.client;
  }

  /**
   * Get current price
   */
  async getPrice(): Promise<SimplePriceData> {
    try {
      const result = await this.client.readContract({
        address: this.contractAddress,
        functionName: 'get_price',
        args: [],
      });

      return result as SimplePriceData;
    } catch (error: any) {
      throw new Error(`Failed to get price: ${error.message}`);
    }
  }

  /**
   * Get price as number
   */
  async getPriceNumber(): Promise<number> {
    const data = await this.getPrice();
    return parseFloat(data.price);
  }

  /**
   * Update price (trigger consensus fetch)
   */
  async updatePrice(): Promise<string> {
    try {
      const account = (this.client as any).account;
      if (!account) {
        throw new Error('Client account not available');
      }

      const txHash = await this.client.writeContract({
        account,
        address: this.contractAddress,
        functionName: 'update_price',
        args: [],
        value: 0n,
      });

      return txHash;
    } catch (error: any) {
      throw new Error(`Failed to update price: ${error.message}`);
    }
  }

  /**
   * Wait for transaction to finalize
   */
  async waitForFinalization(txHash: string): Promise<any> {
    return await this.client.waitForTransactionReceipt({
      hash: txHash,
      status: 'finalized',
    });
  }

  /**
   * Update price and wait for finalization
   */
  async updatePriceAndWait(): Promise<SimplePriceData> {
    const txHash = await this.updatePrice();
    await this.waitForFinalization(txHash);
    
    // Wait a bit for state to update
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    return await this.getPrice();
  }

  /**
   * Subscribe to price updates
   */
  onUpdate(callback: (data: SimplePriceData) => void): void {
    this.updateCallbacks.add(callback);

    if (!this.pollingInterval) {
      this.startPolling();
    }
  }

  /**
   * Unsubscribe from updates
   */
  offUpdate(callback: (data: SimplePriceData) => void): void {
    this.updateCallbacks.delete(callback);

    if (this.updateCallbacks.size === 0) {
      this.stopPolling();
    }
  }

  /**
   * Start polling for updates
   */
  private startPolling(intervalMs: number = 5000): void {
    let lastPrice: string | null = null;

    this.pollingInterval = setInterval(async () => {
      try {
        const currentPrice = await this.getPrice();

        if (lastPrice === null || currentPrice.price !== lastPrice) {
          lastPrice = currentPrice.price;
          this.notifyCallbacks(currentPrice);
        }
      } catch (error) {
        console.error('Error polling price:', error);
      }
    }, intervalMs);
  }

  /**
   * Stop polling
   */
  private stopPolling(): void {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
      this.pollingInterval = undefined;
    }
  }

  /**
   * Notify all callbacks
   */
  private notifyCallbacks(data: SimplePriceData): void {
    this.updateCallbacks.forEach((callback) => {
      try {
        callback(data);
      } catch (error) {
        console.error('Error in update callback:', error);
      }
    });
  }

  /**
   * Cleanup
   */
  destroy(): void {
    this.stopPolling();
    this.updateCallbacks.clear();
  }
}

