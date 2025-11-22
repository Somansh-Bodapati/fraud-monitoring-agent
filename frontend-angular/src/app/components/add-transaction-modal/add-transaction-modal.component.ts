import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatDialogRef } from '@angular/material/dialog';
import { TransactionService } from '../../services/transaction.service';

@Component({
  selector: 'app-add-transaction-modal',
  templateUrl: './add-transaction-modal.component.html',
  styleUrls: ['./add-transaction-modal.component.scss']
})
export class AddTransactionModalComponent {
  transactionForm: FormGroup;
  loading = false;

  constructor(
    private fb: FormBuilder,
    private dialogRef: MatDialogRef<AddTransactionModalComponent>,
    private transactionService: TransactionService
  ) {
    this.transactionForm = this.fb.group({
      amount: ['', [Validators.required, Validators.min(0.01)]],
      merchant: [''],
      description: [''],
      date: [new Date(), Validators.required],
      currency: ['USD']
    });
  }

  onSubmit(): void {
    if (this.transactionForm.valid) {
      this.loading = true;
      const formValue = this.transactionForm.value;
      
      this.transactionService.createTransaction({
        amount: formValue.amount,
        merchant: formValue.merchant,
        description: formValue.description,
        date: formValue.date.toISOString(),
        currency: formValue.currency,
        source: 'manual'
      }).subscribe({
        next: () => {
          this.dialogRef.close(true);
        },
        error: () => {
          this.loading = false;
        }
      });
    }
  }

  onCancel(): void {
    this.dialogRef.close();
  }
}

