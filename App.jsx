import './App.css'

function App() {
  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <h1 className="text-4xl font-bold text-blue-600 mb-4">
        Exchange Rate Forecasting Dashboard
      </h1>
      <p className="text-lg text-gray-700 mb-8">
        Real-time AI-powered exchange rate predictions with sentiment analysis
      </p>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-lg">
          <h2 className="text-xl font-semibold mb-2">Current Rate</h2>
          <div className="text-3xl font-bold text-green-600">1.0545</div>
          <div className="text-sm text-gray-500">USD/EUR</div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-lg">
          <h2 className="text-xl font-semibold mb-2">24h Change</h2>
          <div className="text-3xl font-bold text-green-600">+0.0023</div>
          <div className="text-sm text-gray-500">+0.218%</div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-lg">
          <h2 className="text-xl font-semibold mb-2">Accuracy</h2>
          <div className="text-3xl font-bold text-blue-600">84.7%</div>
          <div className="text-sm text-gray-500">Last 7 days</div>
        </div>
      </div>
      
      <div className="mt-8 bg-white p-6 rounded-lg shadow-lg">
        <h2 className="text-2xl font-semibold mb-4">Features</h2>
        <ul className="space-y-2">
          <li className="flex items-center">
            <span className="w-2 h-2 bg-blue-600 rounded-full mr-3"></span>
            AI-powered forecasting with ensemble models
          </li>
          <li className="flex items-center">
            <span className="w-2 h-2 bg-green-600 rounded-full mr-3"></span>
            Real-time data streaming and updates
          </li>
          <li className="flex items-center">
            <span className="w-2 h-2 bg-purple-600 rounded-full mr-3"></span>
            News sentiment analysis integration
          </li>
          <li className="flex items-center">
            <span className="w-2 h-2 bg-yellow-600 rounded-full mr-3"></span>
            MongoDB Cloud backend storage
          </li>
        </ul>
      </div>
    </div>
  )
}

export default App

