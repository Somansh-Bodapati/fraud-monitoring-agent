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
  currentUserRole: string | null = null;
  entitlements: any = {};

  displayedColumns: string[] = ['merchant', 'category', 'date', 'amount', 'status', 'anomaly', 'actions'];

  constructor(
    private transactionService: TransactionService,
    private dialog: MatDialog
  ) { }

  ngOnInit(): void {
    this.loadCurrentUser();
    this.loadEntitlements();
    this.loadTransactions();
  }

  loadCurrentUser(): void {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      const user = JSON.parse(userStr);
      this.currentUserRole = user.role;
    }
  }

  loadEntitlements(): void {
    this.transactionService.getEntitlements().subscribe({
      next: (entitlements) => {
        this.entitlements = entitlements;
      }
    });
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

  isAdmin(): boolean {
    return this.currentUserRole === 'ADMIN';
  }

  canApprove(): boolean {
    return this.entitlements?.transactions?.canApprove || false;
  }

  canReject(): boolean {
    return this.entitlements?.transactions?.canReject || false;
  }

  canDelete(): boolean {
    return this.entitlements?.transactions?.canDelete || false;
  }

  approveTransaction(transaction: Transaction): void {
    if (confirm(`Approve transaction of $${transaction.amount} from ${transaction.merchant || 'Unknown merchant'}?`)) {
      this.transactionService.updateTransactionStatus(transaction.id, 'APPROVED').subscribe({
        next: () => {
          this.loadTransactions();
        },
        error: (err) => {
          alert('Error approving transaction: ' + (err.error?.message || 'Unknown error'));
        }
      });
    }
  }

  rejectTransaction(transaction: Transaction): void {
    if (confirm(`Reject transaction of $${transaction.amount} from ${transaction.merchant || 'Unknown merchant'}?`)) {
      this.transactionService.updateTransactionStatus(transaction.id, 'REJECTED').subscribe({
        next: () => {
          this.loadTransactions();
        },
        error: (err) => {
          alert('Error rejecting transaction: ' + (err.error?.message || 'Unknown error'));
        }
      });
    }
  }

  deleteTransaction(transaction: Transaction): void {
    if (confirm('Are you sure you want to delete this transaction? This action cannot be undone.')) {
      this.transactionService.deleteTransaction(transaction.id).subscribe({
        next: () => {
          this.loadTransactions();
        },
        error: (err) => {
          alert('Error deleting transaction: ' + (err.error?.message || 'Unknown error'));
        }
      });
    }
  }
}

