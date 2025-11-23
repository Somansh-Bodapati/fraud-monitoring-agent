import { Component, OnInit } from '@angular/core';
import { DashboardService } from '../../services/dashboard.service';
import { ChartData, ChartOptions } from 'chart.js';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit {
  stats: any = null;
  loading = false;

  // Pie Chart for spending by category
  categoryChartData: ChartData<'pie'> = {
    labels: [],
    datasets: [{
      data: [],
      backgroundColor: [
        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
        '#FF9F40', '#FF6384', '#C9CBCF', '#4BC0C0', '#FF6384'
      ]
    }]
  };

  categoryChartOptions: ChartOptions<'pie'> = {
    responsive: true,
    plugins: {
      legend: {
        position: 'right',
        labels: { color: '#ffffff' }
      },
      title: {
        display: true,
        text: 'Spending by Category',
        color: '#ffffff'
      }
    }
  };

  // Bar Chart for category spending amounts
  spendChartData: ChartData<'bar'> = {
    labels: [],
    datasets: [{
      label: 'Total Spend ($)',
      data: [],
      backgroundColor: '#36A2EB'
    }]
  };

  spendChartOptions: ChartOptions<'bar'> = {
    responsive: true,
    plugins: {
      legend: {
        labels: { color: '#ffffff' }
      },
      title: {
        display: true,
        text: 'Spending by Category',
        color: '#ffffff'
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: { color: '#ffffff' },
        grid: { color: 'rgba(255, 255, 255, 0.1)' }
      },
      x: {
        ticks: { color: '#ffffff' },
        grid: { color: 'rgba(255, 255, 255, 0.1)' }
      }
    }
  };

  constructor(private dashboardService: DashboardService) { }

  ngOnInit(): void {
    this.loadStats();
  }

  loadStats(): void {
    this.loading = true;
    this.dashboardService.getStats().subscribe({
      next: (data) => {
        this.stats = data;
        this.processChartData(data);
        this.loading = false;
      },
      error: () => {
        this.loading = false;
      }
    });
  }

  processChartData(data: any): void {
    if (data.categoryBreakdown) {
      const categories = Object.keys(data.categoryBreakdown);
      const counts: number[] = [];
      const totals: number[] = [];

      categories.forEach(cat => {
        counts.push(data.categoryBreakdown[cat].count);
        totals.push(data.categoryBreakdown[cat].total);
      });

      // Format category names for display
      const formattedCategories = categories.map(cat =>
        cat.split('_').map(word =>
          word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
        ).join(' ')
      );

      // Update pie chart
      this.categoryChartData = {
        labels: formattedCategories,
        datasets: [{
          data: totals,
          backgroundColor: [
            '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
            '#FF9F40', '#FF6384', '#C9CBCF', '#4BC0C0', '#FF6384'
          ]
        }]
      };

      // Update bar chart
      this.spendChartData = {
        labels: formattedCategories,
        datasets: [{
          label: 'Total Spend ($)',
          data: totals,
          backgroundColor: '#36A2EB'
        }]
      };
    }
  }
}

