/**
 * Charts Utility Module
 * Provides Chart.js initialization and theming for Dreambook Salon
 * Uses black and gold color scheme (#d4af37 gold, #1a1a1a black)
 */

const chartUtils = {
  // Color palette matching black and gold theme
  colors: {
    primary: '#d4af37',    // Gold
    primaryLight: '#ffd700', // Light gold
    primaryDark: '#b8964a', // Dark gold
    accent: '#1a1a1a',     // Black
    accentLight: '#333333', // Light black
    success: '#28a745',    // Green
    danger: '#dc3545',     // Red
    warning: '#ffc107',    // Yellow
    info: '#17a2b8',       // Cyan
    background: '#faf8f5', // Cream
    border: '#e5e5e5',     // Light gray
    text: '#1a1a1a',       // Dark text
    muted: '#8b8b8b',      // Muted text
  },

  // Default chart options with black and gold theme
  defaultOptions: {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        display: true,
        labels: {
          font: {
            family: "'Inter', sans-serif",
            size: 12,
            weight: '500',
          },
          color: '#1a1a1a',
          padding: 15,
          usePointStyle: true,
        },
      },
      tooltip: {
        backgroundColor: 'rgba(26, 26, 26, 0.9)',
        titleColor: '#d4af37',
        bodyColor: '#ffffff',
        borderColor: '#d4af37',
        borderWidth: 1,
        padding: 12,
        titleFont: {
          weight: 'bold',
          size: 13,
        },
        bodyFont: {
          size: 12,
        },
      },
    },
    scales: {
      y: {
        ticks: {
          color: '#8b8b8b',
          font: {
            size: 11,
          },
        },
        grid: {
          color: 'rgba(212, 175, 55, 0.1)',
        },
      },
      x: {
        ticks: {
          color: '#8b8b8b',
          font: {
            size: 11,
          },
        },
        grid: {
          color: 'rgba(212, 175, 55, 0.05)',
        },
      },
    },
  },

  /**
   * Create Weekly Seasonal Pattern Chart
   * Displays 7-day pattern with today highlighted
   * @param {string} canvasId - HTML canvas element ID
   * @param {Object} data - Chart data {dates: [...], values: [...], today: 'YYYY-MM-DD'}
   * @returns {Chart} Chart.js instance
   */
  createWeeklySeasonalChart(canvasId, data) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
      console.error(`Canvas with ID "${canvasId}" not found`);
      return null;
    }

    const ctx = canvas.getContext('2d');

    // Find today's index to highlight it
    const todayIndex = data.dates.findIndex(date => date === data.today);

    // Create gradient for the line
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, 'rgba(212, 175, 55, 0.3)');
    gradient.addColorStop(1, 'rgba(212, 175, 55, 0.05)');

    const chart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: data.dates.map(date => {
          const d = new Date(date);
          return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        }),
        datasets: [
          {
            label: 'Daily Revenue',
            data: data.values,
            borderColor: '#d4af37',
            backgroundColor: gradient,
            borderWidth: 3,
            pointRadius: 6,
            pointHoverRadius: 8,
            pointBackgroundColor: function(context) {
              // Highlight today's point
              return context.dataIndex === todayIndex ? '#d4af37' : '#d4af37';
            },
            pointBorderColor: function(context) {
              // Thicker border for today
              return context.dataIndex === todayIndex ? '#b8964a' : 'transparent';
            },
            pointBorderWidth: function(context) {
              return context.dataIndex === todayIndex ? 3 : 0;
            },
            tension: 0.4,
            fill: true,
          },
        ],
      },
      options: {
        ...this.defaultOptions,
        plugins: {
          ...this.defaultOptions.plugins,
          title: {
            display: true,
            text: 'Weekly Seasonal Pattern',
            color: '#1a1a1a',
            font: {
              size: 16,
              weight: 'bold',
            },
            padding: 20,
          },
          annotation: {
            // Custom annotation for today
            drawTime: 'afterDatasetsDraw',
          },
        },
      },
      plugins: [
        {
          id: 'todayLine',
          afterDraw(chart) {
            const ctx = chart.ctx;
            const xScale = chart.scales.x;
            const yScale = chart.scales.y;

            if (todayIndex >= 0 && todayIndex < chart.data.labels.length) {
              const x = xScale.getPixelForValue(todayIndex);
              const top = yScale.top;
              const bottom = yScale.bottom;

              // Draw vertical line for today
              ctx.strokeStyle = 'rgba(212, 175, 55, 0.3)';
              ctx.lineWidth = 2;
              ctx.setLineDash([5, 5]);
              ctx.beginPath();
              ctx.moveTo(x, top);
              ctx.lineTo(x, bottom);
              ctx.stroke();
              ctx.setLineDash([]);

              // Draw "Today" label
              ctx.fillStyle = '#d4af37';
              ctx.font = 'bold 12px "Inter", sans-serif';
              ctx.textAlign = 'center';
              ctx.fillText('TODAY', x, top - 10);
            }
          },
        },
      ],
    });

    return chart;
  },

  /**
   * Create Monthly Service Demand Chart
   * Line chart showing demand by service over time
   * @param {string} canvasId - HTML canvas element ID
   * @param {Object} data - Chart data {months: [...], services: [{name, monthlyData, color}, ...]}
   * @returns {Chart} Chart.js instance
   */
  createMonthlyServiceChart(canvasId, data) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
      console.error(`Canvas with ID "${canvasId}" not found`);
      return null;
    }

    const ctx = canvas.getContext('2d');

    // Generate datasets for each service
    const datasets = data.services.map((service, index) => ({
      label: service.name,
      data: service.monthlyData,
      borderColor: service.color || this.colors.primary,
      backgroundColor: `${service.color || this.colors.primary}15`,
      borderWidth: 2,
      pointRadius: 5,
      pointHoverRadius: 7,
      pointBackgroundColor: service.color || this.colors.primary,
      tension: 0.4,
      fill: true,
    }));

    const chart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: data.months || [],
        datasets: datasets,
      },
      options: {
        ...this.defaultOptions,
        plugins: {
          ...this.defaultOptions.plugins,
          title: {
            display: true,
            text: 'Monthly Demand by Service',
            color: '#1a1a1a',
            font: {
              size: 16,
              weight: 'bold',
            },
            padding: 20,
          },
        },
      },
    });

    return chart;
  },

  /**
   * Create Revenue vs Cancellations Comparison Chart
   * Bar chart comparing revenue and cancellations over time
   * @param {string} canvasId - HTML canvas element ID
   * @param {Object} data - Chart data {months: [...], revenue: [...], cancellations: [...]}
   * @returns {Chart} Chart.js instance
   */
  createRevenueVsCancellationsChart(canvasId, data) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
      console.error(`Canvas with ID "${canvasId}" not found`);
      return null;
    }

    const ctx = canvas.getContext('2d');

    const chart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: data.months || [],
        datasets: [
          {
            label: 'Revenue',
            data: data.revenue || [],
            backgroundColor: '#d4af37',
            borderColor: '#b8964a',
            borderWidth: 1,
            borderRadius: 6,
            barPercentage: 0.7,
          },
          {
            label: 'Cancellations',
            data: data.cancellations || [],
            backgroundColor: '#dc3545',
            borderColor: '#c82333',
            borderWidth: 1,
            borderRadius: 6,
            barPercentage: 0.7,
          },
        ],
      },
      options: {
        ...this.defaultOptions,
        plugins: {
          ...this.defaultOptions.plugins,
          title: {
            display: true,
            text: 'Revenue vs Cancellations',
            color: '#1a1a1a',
            font: {
              size: 16,
              weight: 'bold',
            },
            padding: 20,
          },
        },
        scales: {
          ...this.defaultOptions.scales,
          x: {
            ...this.defaultOptions.scales.x,
            stacked: false,
          },
          y: {
            ...this.defaultOptions.scales.y,
            stacked: false,
            beginAtZero: true,
          },
        },
      },
    });

    return chart;
  },

  /**
   * Create Utilization by Stylist Chart
   * Horizontal bar chart showing stylist utilization rates
   * @param {string} canvasId - HTML canvas element ID
   * @param {Object} data - Chart data {stylists: [...], utilization: [...]}
   * @returns {Chart} Chart.js instance
   */
  createUtilizationChart(canvasId, data) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
      console.error(`Canvas with ID "${canvasId}" not found`);
      return null;
    }

    const ctx = canvas.getContext('2d');

    const chart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: data.stylists || [],
        datasets: [
          {
            label: 'Utilization %',
            data: data.utilization || [],
            backgroundColor: '#d4af37',
            borderColor: '#b8964a',
            borderWidth: 1,
            borderRadius: 6,
          },
        ],
      },
      options: {
        ...this.defaultOptions,
        indexAxis: 'y',
        plugins: {
          ...this.defaultOptions.plugins,
          title: {
            display: true,
            text: 'Stylist Utilization Rate',
            color: '#1a1a1a',
            font: {
              size: 16,
              weight: 'bold',
            },
            padding: 20,
          },
        },
        scales: {
          ...this.defaultOptions.scales,
          x: {
            ...this.defaultOptions.scales.x,
            min: 0,
            max: 100,
            ticks: {
              callback: function(value) {
                return value + '%';
              },
            },
          },
        },
      },
    });

    return chart;
  },

  /**
   * Fetch chart data from API endpoint
   * @param {string} url - API endpoint URL
   * @returns {Promise<Object>} Chart data
   */
  async fetchChartData(url) {
    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching chart data:', error);
      return null;
    }
  },

  /**
   * Initialize all charts on a page
   * Looks for data-chart attributes and creates charts accordingly
   */
  initializeAllCharts() {
    const chartElements = document.querySelectorAll('[data-chart-type]');

    chartElements.forEach(async (element) => {
      const chartType = element.dataset.chartType;
      const dataUrl = element.dataset.dataUrl;
      const canvasId = element.id;

      if (!dataUrl) {
        console.warn(`Chart element ${canvasId} has no data-url attribute`);
        return;
      }

      const data = await this.fetchChartData(dataUrl);
      if (!data) {
        console.error(`Failed to load data for chart ${canvasId}`);
        return;
      }

      switch (chartType) {
        case 'weekly':
          this.createWeeklySeasonalChart(canvasId, data);
          break;
        case 'service-demand':
          this.createMonthlyServiceChart(canvasId, data);
          break;
        case 'revenue-cancellations':
          this.createRevenueVsCancellationsChart(canvasId, data);
          break;
        case 'utilization':
          this.createUtilizationChart(canvasId, data);
          break;
        default:
          console.warn(`Unknown chart type: ${chartType}`);
      }
    });
  },

  /**
   * Format currency value for chart display
   * @param {number} value - Value in currency units
   * @returns {string} Formatted currency string
   */
  formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(value);
  },

  /**
   * Format percentage value
   * @param {number} value - Value as percentage (0-100)
   * @returns {string} Formatted percentage string
   */
  formatPercent(value) {
    return `${Math.round(value)}%`;
  },

  /**
   * Generate gradient for chart background
   * @param {CanvasRenderingContext2D} ctx - Canvas context
   * @param {string} startColor - Start color hex
   * @param {string} endColor - End color hex
   * @returns {CanvasGradient} Gradient object
   */
  createGradient(ctx, startColor, endColor) {
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, startColor);
    gradient.addColorStop(1, endColor);
    return gradient;
  },
};

// Auto-initialize charts when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  if (typeof chartUtils !== 'undefined' && chartUtils.initializeAllCharts) {
    chartUtils.initializeAllCharts();
  }
});
