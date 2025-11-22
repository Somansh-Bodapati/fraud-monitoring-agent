import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { TransactionService, Transaction } from '../../services/transaction.service';
import { AddTransactionModalComponent } from '../add-transaction-modal/add-transaction-modal.component';
import { format } from 'date-fns';

@Component({
  selector: 'app-transactions',
  templateUrl: './transactions.component.html',
  styleUrls: ['./transactions.component.scss']
})
export class TransactionsComponent implements OnInit {
  transactions: Transaction[] = [];
  loading = false;

  displayedColumns: string[] = ['merchant', 'category', 'date', 'amount', 'status', 'anomaly'];

  constructor(
    private transactionService: TransactionService,
    private dialog: MatDialog
  ) {}

  ngOnInit(): void {
    this.loadTransactions();
  }

  loadTransactions(): void {
    this.loading = true;
    this.transactionService.getTransactions().subscribe({
      next: (response) => {
        this.transactions = response.content || response || [];
        this.loading = false;
      },
      error: () => {
        this.loading = false;
      }
    });
  }

  openAddTransactionModal(): void {
    const dialogRef = this.dialog.open(AddTransactionModalComponent, {
      width: '500px'
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loadTransactions();
      }
    });
  }

  formatDate(date: string): string {
    return format(new Date(date), 'MMM dd, yyyy');
  }
}

