/**
 * GenLayer Oracle SDK
 * 
 * TypeScript SDK for interacting with GenLayer oracle contracts
 */
import { GenLayerClient, GenLayerChain, Address } from 'genlayer-js';

export interface OracleStatus {
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

export interface UpdateParams {
  city?: string;
  lat?: string;
  lon?: string;
  newsLimit?: number;
}

type UpdateCallback = (data: OracleStatus) => void;

export class OracleSDK {
  private contractAddress: Address;
  private chain: GenLayerChain;
  private client: GenLayerClient<GenLayerChain>;
  private updateCallbacks: Set<UpdateCallback> = new Set();
  private pollingInterval?: NodeJS.Timeout;

  constructor(options: {
    contractAddress: Address;
    chain: GenLayerChain;
    client: GenLayerClient<GenLayerChain>;
  }) {
    this.contractAddress = options.contractAddress;
    this.chain = options.chain;
    this.client = options.client;
  }

  /**
   * Get current oracle status
   */
  async getStatus(): Promise<OracleStatus> {
    try {
      const result = await this.client.readContract({
        address: this.contractAddress,
        functionName: 'get_status',
        args: [],
        jsonSafeReturn: true,
      });

      return result as OracleStatus;
    } catch (error: any) {
      throw new Error(`Failed to get oracle status: ${error.message}`);
    }
  }

  /**
   * Get ETH price
   */
  async getPrice(symbol: string = 'ETH'): Promise<number> {
    const status = await this.getStatus();
    return parseFloat(status.price.eth_usd);
  }

  /**
   * Get weather data
   */
  async getWeather(): Promise<OracleStatus['weather']> {
    const status = await this.getStatus();
    return status.weather;
  }

  /**
   * Get news count
   */
  async getNews(): Promise<number> {
    const status = await this.getStatus();
    return status.news.count;
  }

  /**
   * Trigger oracle update
   */
  async updateOracle(params?: UpdateParams): Promise<string> {
    try {
      const txHash = await this.client.writeContract({
        account: this.client.account,
        address: this.contractAddress,
        functionName: 'update_all',
        args: [
          params?.city || 'Hanoi',
          params?.lat || '21.0245',
          params?.lon || '105.8412',
          params?.newsLimit || 3,
        ],
        value: 0n,
      });

      return txHash;
    } catch (error: any) {
      throw new Error(`Failed to update oracle: ${error.message}`);
    }
  }

  /**
   * Subscribe to oracle updates
   */
  onUpdate(callback: UpdateCallback): void {
    this.updateCallbacks.add(callback);

    // Start polling if not already started
    if (!this.pollingInterval) {
      this.startPolling();
    }
  }

  /**
   * Unsubscribe from updates
   */
  offUpdate(callback: UpdateCallback): void {
    this.updateCallbacks.delete(callback);

    // Stop polling if no callbacks left
    if (this.updateCallbacks.size === 0) {
      this.stopPolling();
    }
  }

  /**
   * Start polling for updates
   */
  private startPolling(intervalMs: number = 5000): void {
    let lastStatus: OracleStatus | null = null;

    this.pollingInterval = setInterval(async () => {
      try {
        const currentStatus = await this.getStatus();

        // Check if status changed
        if (lastStatus === null || JSON.stringify(lastStatus) !== JSON.stringify(currentStatus)) {
          lastStatus = currentStatus;
          this.notifyCallbacks(currentStatus);
        }
      } catch (error) {
        console.error('Error polling oracle:', error);
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
  private notifyCallbacks(data: OracleStatus): void {
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

