import { Component, OnInit } from '@angular/core';
import { AlertService, Alert } from '../../services/alert.service';
import { format } from 'date-fns';

@Component({
  selector: 'app-alerts',
  templateUrl: './alerts.component.html',
  styleUrls: ['./alerts.component.scss']
})
export class AlertsComponent implements OnInit {
  alerts: Alert[] = [];
  loading = false;

  constructor(private alertService: AlertService) {}

  ngOnInit(): void {
    this.loadAlerts();
  }

  loadAlerts(): void {
    this.loading = true;
    this.alertService.getAlerts().subscribe({
      next: (data) => {
        this.alerts = data;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
      }
    });
  }

  markAsRead(alert: Alert): void {
    this.alertService.markAsRead(alert.id).subscribe({
      next: () => {
        alert.isRead = true;
      }
    });
  }

  formatDate(date: string): string {
    return format(new Date(date), 'MMM dd, yyyy HH:mm');
  }

  getSeverityColor(severity: string): string {
    switch (severity.toLowerCase()) {
      case 'critical': return 'warn';
      case 'high': return 'accent';
      case 'medium': return 'primary';
      default: return '';
    }
  }
}

