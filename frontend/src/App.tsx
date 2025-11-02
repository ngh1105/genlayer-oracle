import { useEffect, useState } from 'react'
import './App.css'
import { createClient, createAccount, Address } from 'genlayer-js'
import { studionet } from 'genlayer-js/chains'

interface OracleStatus {
  price: { eth_usd: string; source: string }
  weather: { temperature: string; condition: string; city: string }
  news: { count: number }
}

interface SimplePriceData {
  price: string
  source: string
}

type ContractType = 'oracle' | 'simple'

function App() {
  const [client, setClient] = useState<any>(null)
  const [account, setAccount] = useState<any>(null)
  const [contractAddress, setContractAddress] = useState<string>('')
  const [contractType, setContractType] = useState<ContractType>('simple')
  const [status, setStatus] = useState<string>('')
  const [oracleData, setOracleData] = useState<OracleStatus | null>(null)
  const [simplePriceData, setSimplePriceData] = useState<SimplePriceData | null>(null)
  const [loading, setLoading] = useState(false)
  const [updating, setUpdating] = useState(false)
  
  // Default contract addresses
  const DEFAULT_SIMPLE_CONTRACT = '0xe328378CAF086ae0a6458395C9919a4137fCb888'
  const DEFAULT_ORACLE_CONTRACT = '0xe0E45EC84BB780BB1cccAc1B0CB09E507eF37147'

  useEffect(() => {
    const init = async () => {
      try {
        const acc = createAccount()
        const cli = createClient({ chain: studionet, account: acc })
        setAccount(acc)
        setClient(cli)
        setStatus(`Connected to ${studionet.name}`)
      } catch (e: any) {
        setStatus(`Error: ${e?.message ?? String(e)}`)
      }
    }
    init()
  }, [])

  const readContractStatus = async () => {
    if (!client || !contractAddress) {
      setStatus('Please set contract address first')
      return
    }

    setLoading(true)
    try {
      if (contractType === 'simple') {
        // Simple Price Feed contract
        const result = await client.readContract({
          address: contractAddress as Address,
          functionName: 'get_price',
          args: [],
        })
        setSimplePriceData(result as SimplePriceData)
        setStatus('Price loaded successfully')
      } else {
        // Oracle Consumer contract
        const result = await client.readContract({
          address: contractAddress as Address,
          functionName: 'get_status',
          args: [],
        })
        setOracleData(result as OracleStatus)
        setStatus('Status loaded successfully')
      }
    } catch (e: any) {
      setStatus(`Error reading contract: ${e?.message ?? String(e)}`)
    } finally {
      setLoading(false)
    }
  }

  const updateContract = async () => {
    if (!client || !account || !contractAddress) {
      setStatus('Please set contract address and ensure account is ready')
      return
    }

    setUpdating(true)
    setStatus('Updating contract data...')
    try {
      let txHash: string
      
      if (contractType === 'simple') {
        // Simple Price Feed - update_price()
        txHash = await client.writeContract({
          account,
          address: contractAddress as Address,
          functionName: 'update_price',
          args: [],
          value: 0n,
        })
      } else {
        // Oracle Consumer - update_all()
        txHash = await client.writeContract({
          account,
          address: contractAddress as Address,
          functionName: 'update_all',
          args: ['Hanoi', '21.0245', '105.8412', 3],
          value: 0n,
        })
      }
      
      setStatus(`Transaction sent: ${txHash}. Waiting for finalization...`)
      
      // Wait for transaction receipt
      const receipt = await client.waitForTransactionReceipt({
        hash: txHash,
        status: 'finalized',
      })
      
      if (receipt.status === 'finalized') {
        setStatus('Contract updated successfully!')
        // Refresh status after update
        await readContractStatus()
      }
    } catch (e: any) {
      setStatus(`Error updating contract: ${e?.message ?? String(e)}`)
    } finally {
      setUpdating(false)
    }
  }
  
  useEffect(() => {
    // Set default contract address when contract type changes
    if (contractType === 'simple' && !contractAddress) {
      setContractAddress(DEFAULT_SIMPLE_CONTRACT)
    } else if (contractType === 'oracle' && !contractAddress) {
      setContractAddress(DEFAULT_ORACLE_CONTRACT)
    }
  }, [contractType, contractAddress])

  return (
    <div style={{ padding: 24, maxWidth: 800, margin: '0 auto' }}>
      <h1>GenLayer Oracle Contracts</h1>
      
      <div style={{ marginBottom: 16 }}>
        <label>
          Contract Type:
          <select
            value={contractType}
            onChange={(e) => setContractType(e.target.value as ContractType)}
            style={{ width: '100%', padding: 8, marginTop: 4 }}
          >
            <option value="simple">Simple Price Feed ({DEFAULT_SIMPLE_CONTRACT.substring(0, 10)}...)</option>
            <option value="oracle">Oracle Consumer ({DEFAULT_ORACLE_CONTRACT.substring(0, 10)}...)</option>
          </select>
        </label>
      </div>
      
      <div style={{ marginBottom: 16 }}>
        <label>
          Contract Address:
          <input
            type="text"
            value={contractAddress}
            onChange={(e) => setContractAddress(e.target.value)}
            placeholder={contractType === 'simple' ? DEFAULT_SIMPLE_CONTRACT : DEFAULT_ORACLE_CONTRACT}
            style={{ width: '100%', padding: 8, marginTop: 4 }}
          />
        </label>
      </div>

      <div style={{ marginBottom: 16 }}>
        <button onClick={readContractStatus} disabled={loading || !contractAddress}>
          {loading ? 'Loading...' : contractType === 'simple' ? 'Read Price' : 'Read Status'}
        </button>
        <button 
          onClick={updateContract} 
          disabled={updating || !contractAddress}
          style={{ marginLeft: 8 }}
        >
          {updating ? 'Updating...' : contractType === 'simple' ? 'Update Price' : 'Update Oracle'}
        </button>
      </div>

      <p style={{ color: status.includes('Error') ? 'red' : status.includes('successfully') || status.includes('Ready') ? 'green' : 'black' }}>
        {status || 'Ready'}
      </p>

      {simplePriceData && contractType === 'simple' && (
        <div style={{ marginTop: 24, padding: 16, border: '1px solid #ccc', borderRadius: 8 }}>
          <h3>Simple Price Feed (On-Chain)</h3>
          <div>
            <strong>ETH Price</strong>: ${simplePriceData.price} ({simplePriceData.source})
          </div>
        </div>
      )}

      {oracleData && contractType === 'oracle' && (
        <div style={{ marginTop: 24, padding: 16, border: '1px solid #ccc', borderRadius: 8 }}>
          <h3>Oracle Data (On-Chain)</h3>
          <div>
            <strong>ETH Price</strong>: ${oracleData.price.eth_usd} ({oracleData.price.source})
          </div>
          <div>
            <strong>Weather</strong>: {oracleData.weather.temperature}°C, {oracleData.weather.condition} ({oracleData.weather.city})
          </div>
          <div>
            <strong>News Count</strong>: {oracleData.news.count}
          </div>
        </div>
      )}

      <div style={{ marginTop: 24, padding: 16, backgroundColor: '#f5f5f5', borderRadius: 8 }}>
        <h4>Instructions</h4>
        {contractType === 'simple' ? (
          <ol>
            <li><strong>Simple Price Feed</strong> deployed at: <code>{DEFAULT_SIMPLE_CONTRACT}</code></li>
            <li>Click "Read Price" to view current ETH price</li>
            <li>Click "Update Price" to fetch fresh price (requires consensus)</li>
            <li>Price fetched from Binance with Coingecko fallback</li>
          </ol>
        ) : (
          <ol>
            <li><strong>Oracle Consumer</strong> deployed at: <code>{DEFAULT_ORACLE_CONTRACT}</code></li>
            <li>Click "Read Status" to view current on-chain data (price, weather, news)</li>
            <li>Click "Update Oracle" to fetch fresh data (requires consensus)</li>
            <li>Fetches: ETH price, weather (Hanoi), crypto news count</li>
          </ol>
        )}
      </div>
    </div>
  )
}

export default App
