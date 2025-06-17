import { CheckCircle, Copy, Download } from 'lucide-react';
import React from 'react'

type Props = {
    results: {
        team_id: string;
        items: {
        title: string;
        content: string;
        content_type: string;
        source_url: string;
        author: string;
        user_id: string;
        }[];
        summary: {
        total_items: number;
        content_types: { [key: string]: number };
        sources_processed: number;
        processing_time: string;
        };
    } | null
    logs: {
        id: number;
        message: string;
        type: string;
        timestamp: string;
    }[];
    copyToClipboard: () => void;
    getContentTypeIcon: (type: string) => React.ReactNode;
    downloadResults: () => void;
}

const Results = ({ results,getContentTypeIcon,logs, copyToClipboard, downloadResults }: Props) => {
  return (
    <div className="bg-white rounded-2xl shadow-xl p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-900 flex items-center">
                <CheckCircle className="w-6 h-6 mr-2 text-green-600" />
                Results
              </h2>
              {results && (
                <div className="flex space-x-2">
                  <button
                    onClick={copyToClipboard}
                    className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg"
                    title="Copy JSON"
                  >
                    <Copy className="w-5 h-5" />
                  </button>
                  <button
                    onClick={downloadResults}
                    className="p-2 text-indigo-600 hover:text-indigo-800 hover:bg-indigo-50 rounded-lg"
                    title="Download JSON"
                  >
                    <Download className="w-5 h-5" />
                  </button>
                </div>
              )}
            </div>

            {/* Summary */}
            {/* {results && (
              <div className="mb-6 p-4 bg-green-50 rounded-lg">
                <h3 className="font-semibold text-green-800 mb-2">Scraping Summary</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-green-600">Total Items:</span>
                    <span className="font-semibold ml-2">{results.summary.total_items}</span>
                  </div>
                  <div>
                    <span className="text-green-600">Sources:</span>
                    <span className="font-semibold ml-2">{results.summary.sources_processed}</span>
                  </div>
                  <div>
                    <span className="text-green-600">Processing Time:</span>
                    <span className="font-semibold ml-2">{results.summary.processing_time}</span>
                  </div>
                  <div>
                    <span className="text-green-600">Team ID:</span>
                    <span className="font-semibold ml-2">{results.team_id}</span>
                  </div>
                </div>
                <div className="mt-3">
                  <span className="text-green-600">Content Types:</span>
                  <div className="flex flex-wrap gap-2 mt-1">
                    {Object.entries(results.summary.content_types).map(([type, count]) => (
                      <span key={type} className="inline-flex items-center px-2 py-1 bg-white rounded-full text-xs border">
                        {getContentTypeIcon(type)}
                        <span className="ml-1">{type}: {count}</span>
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            )} */}

            {/* Sample Items */}
            {/* {results && (
              <div className="mb-6">
                <h3 className="font-semibold text-gray-800 mb-3">Sample Items</h3>
                <div className="space-y-3 max-h-64 overflow-y-auto">
                  {results.items.slice(0, 5).map((item, index) => (
                    <div key={index} className="p-3 border border-gray-200 rounded-lg">
                      <div className="flex items-center justify-between mb-1">
                        <h4 className="font-medium text-gray-900 text-sm truncate">{item.title}</h4>
                        <span className="inline-flex items-center px-2 py-1 bg-gray-100 rounded-full text-xs">
                          {getContentTypeIcon(item.content_type)}
                          <span className="ml-1">{item.content_type}</span>
                        </span>
                      </div>
                      <p className="text-xs text-gray-600 mb-1">Author: {item.author}</p>
                      <p className="text-xs text-gray-500 truncate">{item.source_url}</p>
                    </div>
                  ))}
                </div>
              </div>
            )} */}

            {/* Logs */}
            <div>
              <h3 className="font-semibold text-gray-800 mb-3">Activity Log</h3>
              <div className="bg-gray-50 rounded-lg p-3 max-h-48 overflow-y-auto">
                {logs.length === 0 ? (
                  <p className="text-gray-500 text-sm">No activity yet. Click "Start Scraping" to begin.</p>
                ) : (
                  <div className="space-y-1">
                    {logs.map((log) => (
                      <div key={log.id} className="flex items-start space-x-2 text-sm">
                        <span className="text-gray-400 text-xs mt-0.5">{log.timestamp}</span>
                        <span className={`${
                          log.type === 'error' ? 'text-red-600' :
                          log.type === 'success' ? 'text-green-600' :
                          'text-gray-700'
                        }`}>
                          {log.message}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
  )
}

export default Results