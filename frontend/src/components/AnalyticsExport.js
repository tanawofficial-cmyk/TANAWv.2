import React, { useState } from 'react';
import { 
  Download, 
  Share2, 
  FileText, 
  Image, 
  BarChart3, 
  Mail, 
  Link, 
  Copy,
  Check,
  X,
  Settings,
  Calendar,
  User,
  Eye
} from 'lucide-react';

const AnalyticsExport = ({ analysisId, analyticsData, onClose }) => {
  const [exportFormat, setExportFormat] = useState('json');
  const [exportOptions, setExportOptions] = useState({
    includeCharts: true,
    includeData: true,
    includeInsights: true,
    includeMetadata: true,
    dateRange: 'all'
  });
  const [shareOptions, setShareOptions] = useState({
    method: 'link', // 'link', 'email', 'embed'
    expiration: '7d',
    accessLevel: 'view', // 'view', 'edit'
    password: '',
    emailRecipients: ''
  });
  const [isExporting, setIsExporting] = useState(false);
  const [isSharing, setIsSharing] = useState(false);
  const [copied, setCopied] = useState(false);
  const [activeTab, setActiveTab] = useState('export'); // 'export' or 'share'

  const exportFormats = [
    { id: 'json', name: 'JSON', description: 'Complete data with metadata', icon: FileText },
    { id: 'csv', name: 'CSV', description: 'Tabular data for spreadsheets', icon: BarChart3 },
    { id: 'pdf', name: 'PDF Report', description: 'Formatted report with charts', icon: FileText },
    { id: 'excel', name: 'Excel', description: 'Interactive spreadsheet', icon: BarChart3 }
  ];

  const shareMethods = [
    { id: 'link', name: 'Share Link', description: 'Generate a shareable link', icon: Link },
    { id: 'email', name: 'Email Report', description: 'Send via email', icon: Mail },
    { id: 'embed', name: 'Embed Code', description: 'Embed in website', icon: Eye }
  ];

  const handleExport = async () => {
    setIsExporting(true);
    try {
      // Simulate export process
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Here you would call the actual export API
      const exportUrl = `/api/analytics/${analysisId}/export?format=${exportFormat}`;
      
      // Create download link
      const link = document.createElement('a');
      link.href = exportUrl;
      link.download = `analytics-${analysisId}.${exportFormat}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      console.log('Export completed:', exportFormat);
    } catch (error) {
      console.error('Export failed:', error);
    } finally {
      setIsExporting(false);
    }
  };

  const handleShare = async () => {
    setIsSharing(true);
    try {
      // Simulate sharing process
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      if (shareOptions.method === 'link') {
        const shareUrl = `https://tanaw.app/analytics/${analysisId}?access=${shareOptions.accessLevel}`;
        await navigator.clipboard.writeText(shareUrl);
        setCopied(true);
        setTimeout(() => setCopied(false), 3000);
      } else if (shareOptions.method === 'email') {
        // Here you would call the email sharing API
        console.log('Email sharing:', shareOptions.emailRecipients);
      } else if (shareOptions.method === 'embed') {
        const embedCode = `<iframe src="https://tanaw.app/analytics/${analysisId}/embed" width="100%" height="600"></iframe>`;
        await navigator.clipboard.writeText(embedCode);
        setCopied(true);
        setTimeout(() => setCopied(false), 3000);
      }
      
      console.log('Sharing completed:', shareOptions.method);
    } catch (error) {
      console.error('Sharing failed:', error);
    } finally {
      setIsSharing(false);
    }
  };

  const copyToClipboard = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy:', error);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900">Export & Share Analytics</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="w-6 h-6" />
            </button>
          </div>
          
          {/* Tabs */}
          <div className="mt-4 flex space-x-1 bg-gray-100 p-1 rounded-lg">
            <button
              onClick={() => setActiveTab('export')}
              className={`flex-1 py-2 px-4 text-sm font-medium rounded-md transition-colors ${
                activeTab === 'export'
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Download className="w-4 h-4 inline mr-2" />
              Export
            </button>
            <button
              onClick={() => setActiveTab('share')}
              className={`flex-1 py-2 px-4 text-sm font-medium rounded-md transition-colors ${
                activeTab === 'share'
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Share2 className="w-4 h-4 inline mr-2" />
              Share
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6">
          {activeTab === 'export' && (
            <div className="space-y-6">
              {/* Export Format Selection */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-3">Export Format</h3>
                <div className="grid grid-cols-2 gap-3">
                  {exportFormats.map((format) => {
                    const Icon = format.icon;
                    return (
                      <button
                        key={format.id}
                        onClick={() => setExportFormat(format.id)}
                        className={`p-4 border rounded-lg text-left transition-colors ${
                          exportFormat === format.id
                            ? 'border-blue-500 bg-blue-50'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        <div className="flex items-center gap-3">
                          <Icon className={`w-5 h-5 ${
                            exportFormat === format.id ? 'text-blue-600' : 'text-gray-500'
                          }`} />
                          <div>
                            <div className={`font-medium ${
                              exportFormat === format.id ? 'text-blue-900' : 'text-gray-900'
                            }`}>
                              {format.name}
                            </div>
                            <div className={`text-sm ${
                              exportFormat === format.id ? 'text-blue-700' : 'text-gray-500'
                            }`}>
                              {format.description}
                            </div>
                          </div>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Export Options */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-3">Export Options</h3>
                <div className="space-y-3">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={exportOptions.includeCharts}
                      onChange={(e) => setExportOptions(prev => ({ ...prev, includeCharts: e.target.checked }))}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="ml-2 text-sm text-gray-700">Include visualizations and charts</span>
                  </label>
                  
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={exportOptions.includeData}
                      onChange={(e) => setExportOptions(prev => ({ ...prev, includeData: e.target.checked }))}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="ml-2 text-sm text-gray-700">Include raw data</span>
                  </label>
                  
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={exportOptions.includeInsights}
                      onChange={(e) => setExportOptions(prev => ({ ...prev, includeInsights: e.target.checked }))}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="ml-2 text-sm text-gray-700">Include insights and recommendations</span>
                  </label>
                  
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={exportOptions.includeMetadata}
                      onChange={(e) => setExportOptions(prev => ({ ...prev, includeMetadata: e.target.checked }))}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="ml-2 text-sm text-gray-700">Include metadata and configuration</span>
                  </label>
                </div>
              </div>

              {/* Export Button */}
              <div className="pt-4 border-t border-gray-200">
                <button
                  onClick={handleExport}
                  disabled={isExporting}
                  className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {isExporting ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      Exporting...
                    </>
                  ) : (
                    <>
                      <Download className="w-4 h-4" />
                      Export Analytics
                    </>
                  )}
                </button>
              </div>
            </div>
          )}

          {activeTab === 'share' && (
            <div className="space-y-6">
              {/* Share Method Selection */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-3">Share Method</h3>
                <div className="space-y-3">
                  {shareMethods.map((method) => {
                    const Icon = method.icon;
                    return (
                      <button
                        key={method.id}
                        onClick={() => setShareOptions(prev => ({ ...prev, method: method.id }))}
                        className={`w-full p-4 border rounded-lg text-left transition-colors ${
                          shareOptions.method === method.id
                            ? 'border-blue-500 bg-blue-50'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        <div className="flex items-center gap-3">
                          <Icon className={`w-5 h-5 ${
                            shareOptions.method === method.id ? 'text-blue-600' : 'text-gray-500'
                          }`} />
                          <div>
                            <div className={`font-medium ${
                              shareOptions.method === method.id ? 'text-blue-900' : 'text-gray-900'
                            }`}>
                              {method.name}
                            </div>
                            <div className={`text-sm ${
                              shareOptions.method === method.id ? 'text-blue-700' : 'text-gray-500'
                            }`}>
                              {method.description}
                            </div>
                          </div>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Share Options */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-3">Share Settings</h3>
                
                {shareOptions.method === 'link' && (
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Access Level</label>
                      <select
                        value={shareOptions.accessLevel}
                        onChange={(e) => setShareOptions(prev => ({ ...prev, accessLevel: e.target.value }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="view">View Only</option>
                        <option value="edit">View and Export</option>
                      </select>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Expiration</label>
                      <select
                        value={shareOptions.expiration}
                        onChange={(e) => setShareOptions(prev => ({ ...prev, expiration: e.target.value }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="1d">1 Day</option>
                        <option value="7d">7 Days</option>
                        <option value="30d">30 Days</option>
                        <option value="never">Never</option>
                      </select>
                    </div>
                  </div>
                )}

                {shareOptions.method === 'email' && (
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Email Recipients</label>
                      <input
                        type="email"
                        value={shareOptions.emailRecipients}
                        onChange={(e) => setShareOptions(prev => ({ ...prev, emailRecipients: e.target.value }))}
                        placeholder="Enter email addresses separated by commas"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        multiple
                      />
                    </div>
                  </div>
                )}

                {shareOptions.method === 'embed' && (
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Embed Code</label>
                      <div className="relative">
                        <textarea
                          readOnly
                          value={`<iframe src="https://tanaw.app/analytics/${analysisId}/embed" width="100%" height="600"></iframe>`}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-sm font-mono"
                          rows={3}
                        />
                        <button
                          onClick={() => copyToClipboard(`<iframe src="https://tanaw.app/analytics/${analysisId}/embed" width="100%" height="600"></iframe>`)}
                          className="absolute top-2 right-2 p-1 text-gray-500 hover:text-gray-700"
                        >
                          {copied ? <Check className="w-4 h-4 text-green-600" /> : <Copy className="w-4 h-4" />}
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Share Button */}
              <div className="pt-4 border-t border-gray-200">
                <button
                  onClick={handleShare}
                  disabled={isSharing}
                  className="w-full bg-green-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {isSharing ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      Sharing...
                    </>
                  ) : (
                    <>
                      <Share2 className="w-4 h-4" />
                      {shareOptions.method === 'link' ? 'Generate Share Link' : 
                       shareOptions.method === 'email' ? 'Send Email' : 'Copy Embed Code'}
                    </>
                  )}
                </button>
                
                {copied && shareOptions.method === 'link' && (
                  <p className="mt-2 text-sm text-green-600 text-center">
                    Share link copied to clipboard!
                  </p>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AnalyticsExport;
