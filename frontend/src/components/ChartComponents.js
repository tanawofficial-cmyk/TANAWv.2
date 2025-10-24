import React, { useState, useMemo } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  AreaChart,
  Area,
  ScatterChart,
  Scatter,
  ComposedChart,
  Legend,
  RadialBarChart,
  RadialBar,
  FunnelChart,
  Funnel,
  LabelList
} from 'recharts';
import { 
  TrendingUp, 
  TrendingDown, 
  BarChart3, 
  PieChart as PieChartIcon,
  Activity,
  Download,
  Maximize2,
  Minimize2,
  RotateCcw
} from 'lucide-react';

// Color palettes for different chart types
const CHART_COLORS = {
  primary: ['#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#00ff00', '#ff00ff'],
  sales: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4'],
  regional: ['#1e40af', '#059669', '#d97706', '#dc2626', '#7c3aed', '#0891b2'],
  product: ['#1d4ed8', '#047857', '#b45309', '#b91c1c', '#6d28d9', '#0e7490']
};

// Custom tooltip component
const CustomTooltip = ({ active, payload, label, formatValue }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
        <p className="font-medium text-gray-900">{label}</p>
        {payload.map((entry, index) => (
          <p key={index} className="text-sm" style={{ color: entry.color }}>
            {`${entry.dataKey}: ${formatValue ? formatValue(entry.value) : entry.value}`}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

// Sales Trend Chart Component
export const SalesTrendChart = ({ data, title = "Sales Trend", height = 300, expanded = false }) => {
  const [isExpanded, setIsExpanded] = useState(expanded);
  
  const chartData = useMemo(() => {
    if (!data || !Array.isArray(data)) return [];
    return data.map(item => ({
      ...item,
      formatted_date: new Date(item.date || item.month).toLocaleDateString(),
      sales_value: parseFloat(item.sales || item.amount || 0)
    }));
  }, [data]);

  const formatCurrency = (value) => `₱${value.toLocaleString()}`;
  const formatDate = (value) => new Date(value).toLocaleDateString();

  if (!chartData.length) {
    return (
      <div className="flex items-center justify-center h-full text-gray-500">
        <div className="text-center">
          <Activity className="w-8 h-8 mx-auto mb-2 text-gray-400" />
          <p>No sales data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-lg border border-gray-200 ${isExpanded ? 'fixed inset-4 z-50' : ''}`}>
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
            <p className="text-sm text-gray-600">Sales performance over time</p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg"
            >
              {isExpanded ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
            </button>
          </div>
        </div>
      </div>
      
      <div className="p-4">
        <ResponsiveContainer width="100%" height={isExpanded ? 500 : height}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis 
              dataKey="formatted_date" 
              tick={{ fontSize: 12 }}
              tickLine={{ stroke: '#e5e7eb' }}
            />
            <YAxis 
              tick={{ fontSize: 12 }}
              tickLine={{ stroke: '#e5e7eb' }}
              tickFormatter={formatCurrency}
            />
            <Tooltip 
              content={<CustomTooltip formatValue={formatCurrency} />}
              labelFormatter={formatDate}
            />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="sales_value" 
              stroke={CHART_COLORS.sales[0]} 
              strokeWidth={3}
              dot={{ fill: CHART_COLORS.sales[0], strokeWidth: 2, r: 4 }}
              activeDot={{ r: 6, stroke: CHART_COLORS.sales[0], strokeWidth: 2 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

// Product Performance Chart Component
export const ProductPerformanceChart = ({ data, title = "Product Performance", height = 300 }) => {
  const chartData = useMemo(() => {
    if (!data || !Array.isArray(data)) return [];
    return data.map((item, index) => ({
      ...item,
      product_name: item.product || item.name || `Product ${index + 1}`,
      sales_value: parseFloat(item.sales || item.amount || 0),
      quantity_value: parseFloat(item.quantity || item.qty || 0),
      color: CHART_COLORS.product[index % CHART_COLORS.product.length]
    }));
  }, [data]);

  const formatCurrency = (value) => `₱${value.toLocaleString()}`;
  const formatQuantity = (value) => `${value} units`;

  if (!chartData.length) {
    return (
      <div className="flex items-center justify-center h-full text-gray-500">
        <div className="text-center">
          <BarChart3 className="w-8 h-8 mx-auto mb-2 text-gray-400" />
          <p>No product data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200">
      <div className="p-4 border-b border-gray-200">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
          <p className="text-sm text-gray-600">Sales by product category</p>
        </div>
      </div>
      
      <div className="p-4">
        <ResponsiveContainer width="100%" height={height}>
          <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis 
              dataKey="product_name" 
              tick={{ fontSize: 12 }}
              tickLine={{ stroke: '#e5e7eb' }}
              angle={-45}
              textAnchor="end"
              height={80}
            />
            <YAxis 
              tick={{ fontSize: 12 }}
              tickLine={{ stroke: '#e5e7eb' }}
              tickFormatter={formatCurrency}
            />
            <Tooltip 
              content={<CustomTooltip formatValue={formatCurrency} />}
            />
            <Legend />
            <Bar 
              dataKey="sales_value" 
              fill={CHART_COLORS.sales[0]}
              radius={[4, 4, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

// Regional Distribution Chart Component
export const RegionalDistributionChart = ({ data, title = "Regional Distribution", height = 300 }) => {
  const chartData = useMemo(() => {
    if (!data || !Array.isArray(data)) return [];
    return data.map((item, index) => ({
      ...item,
      region_name: item.region || item.name || `Region ${index + 1}`,
      sales_value: parseFloat(item.sales || item.amount || item.value || 0),
      color: CHART_COLORS.regional[index % CHART_COLORS.regional.length]
    }));
  }, [data]);

  const formatCurrency = (value) => `₱${value.toLocaleString()}`;

  if (!chartData.length) {
    return (
      <div className="flex items-center justify-center h-full text-gray-500">
        <div className="text-center">
          <PieChartIcon className="w-8 h-8 mx-auto mb-2 text-gray-400" />
          <p>No regional data available</p>
        </div>
      </div>
    );
  }

  const totalSales = chartData.reduce((sum, item) => sum + item.sales_value, 0);

  return (
    <div className="bg-white rounded-lg border border-gray-200">
      <div className="p-4 border-b border-gray-200">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
          <p className="text-sm text-gray-600">Sales distribution across regions</p>
        </div>
      </div>
      
      <div className="p-4">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <ResponsiveContainer width="100%" height={height}>
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                outerRadius={height * 0.3}
                fill="#8884d8"
                dataKey="sales_value"
                label={({ region_name, percent }) => `${region_name} ${(percent * 100).toFixed(0)}%`}
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip formatValue={formatCurrency} />} />
            </PieChart>
          </ResponsiveContainer>
          
          <div className="flex flex-col justify-center">
            <div className="space-y-3">
              {chartData.map((item, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div 
                      className="w-3 h-3 rounded-full" 
                      style={{ backgroundColor: item.color }}
                    ></div>
                    <span className="text-sm font-medium text-gray-700">{item.region_name}</span>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-semibold text-gray-900">
                      {formatCurrency(item.sales_value)}
                    </div>
                    <div className="text-xs text-gray-500">
                      {((item.sales_value / totalSales) * 100).toFixed(1)}%
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Sales vs Quantity Correlation Chart
export const SalesQuantityCorrelationChart = ({ data, title = "Sales vs Quantity Correlation", height = 300 }) => {
  const chartData = useMemo(() => {
    if (!data || !Array.isArray(data)) return [];
    return data.map(item => ({
      ...item,
      quantity_value: parseFloat(item.quantity || item.qty || 0),
      sales_value: parseFloat(item.sales || item.amount || 0)
    }));
  }, [data]);

  const formatCurrency = (value) => `₱${value.toLocaleString()}`;
  const formatQuantity = (value) => `${value} units`;

  if (!chartData.length) {
    return (
      <div className="flex items-center justify-center h-full text-gray-500">
        <div className="text-center">
          <Activity className="w-8 h-8 mx-auto mb-2 text-gray-400" />
          <p>No correlation data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200">
      <div className="p-4 border-b border-gray-200">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
          <p className="text-sm text-gray-600">Relationship between sales amount and quantity sold</p>
        </div>
      </div>
      
      <div className="p-4">
        <ResponsiveContainer width="100%" height={height}>
          <ScatterChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis 
              type="number" 
              dataKey="quantity_value" 
              name="Quantity" 
              tick={{ fontSize: 12 }}
              tickLine={{ stroke: '#e5e7eb' }}
              tickFormatter={formatQuantity}
            />
            <YAxis 
              type="number" 
              dataKey="sales_value" 
              name="Sales" 
              tick={{ fontSize: 12 }}
              tickLine={{ stroke: '#e5e7eb' }}
              tickFormatter={formatCurrency}
            />
            <Tooltip 
              cursor={{ strokeDasharray: '3 3' }}
              content={<CustomTooltip />}
            />
            <Scatter 
              dataKey="sales_value" 
              fill={CHART_COLORS.sales[0]}
              r={6}
            />
          </ScatterChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

// Composed Chart for Multiple Metrics
export const ComposedMetricsChart = ({ data, title = "Multiple Metrics", height = 300 }) => {
  const chartData = useMemo(() => {
    if (!data || !Array.isArray(data)) return [];
    return data.map(item => ({
      ...item,
      sales_value: parseFloat(item.sales || item.amount || 0),
      quantity_value: parseFloat(item.quantity || item.qty || 0),
      target_value: parseFloat(item.target || 0)
    }));
  }, [data]);

  const formatCurrency = (value) => `₱${value.toLocaleString()}`;
  const formatQuantity = (value) => `${value}`;

  if (!chartData.length) {
    return (
      <div className="flex items-center justify-center h-full text-gray-500">
        <div className="text-center">
          <BarChart3 className="w-8 h-8 mx-auto mb-2 text-gray-400" />
          <p>No metrics data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200">
      <div className="p-4 border-b border-gray-200">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
          <p className="text-sm text-gray-600">Combined view of sales and quantity metrics</p>
        </div>
      </div>
      
      <div className="p-4">
        <ResponsiveContainer width="100%" height={height}>
          <ComposedChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="name" tick={{ fontSize: 12 }} tickLine={{ stroke: '#e5e7eb' }} />
            <YAxis yAxisId="left" tick={{ fontSize: 12 }} tickLine={{ stroke: '#e5e7eb' }} tickFormatter={formatCurrency} />
            <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 12 }} tickLine={{ stroke: '#e5e7eb' }} tickFormatter={formatQuantity} />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Bar yAxisId="left" dataKey="sales_value" fill={CHART_COLORS.sales[0]} />
            <Line yAxisId="right" type="monotone" dataKey="quantity_value" stroke={CHART_COLORS.sales[1]} strokeWidth={2} />
            <Line yAxisId="left" type="monotone" dataKey="target_value" stroke={CHART_COLORS.sales[2]} strokeWidth={2} strokeDasharray="5 5" />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

// Export all chart components
export const ChartComponents = {
  SalesTrendChart,
  ProductPerformanceChart,
  RegionalDistributionChart,
  SalesQuantityCorrelationChart,
  ComposedMetricsChart
};

export default ChartComponents;
