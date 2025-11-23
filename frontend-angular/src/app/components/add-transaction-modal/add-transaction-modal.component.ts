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

  categories = [
    'SOFTWARE_LICENSES',
    'CLOUD_SERVICES',
    'DEVELOPMENT_TOOLS',
    'PAYROLL',
    'OFFICE_SUPPLIES',
    'MARKETING',
    'CONSULTING',
    'TRAINING',
    'HARDWARE',
    'TRAVEL',
    'OTHER'
  ];

  submitting = false;

  constructor(
    private fb: FormBuilder,
    private dialogRef: MatDialogRef<AddTransactionModalComponent>,
    private transactionService: TransactionService
  ) {
    this.transactionForm = this.fb.group({
      amount: ['', [Validators.required, Validators.min(0.01)]],
      merchant: [''],
      description: [''],
      category: ['OTHER', Validators.required],
      date: [new Date(), Validators.required],
      currency: ['USD']
    });
  }

  onSubmit(event?: Event): void {
    if (event) {
      event.preventDefault();
      event.stopPropagation();
    }

    if (this.transactionForm.valid && !this.loading && !this.submitting) {
      this.loading = true;
      this.submitting = true;
      const formValue = this.transactionForm.value;

      this.transactionService.createTransaction({
        amount: formValue.amount,
        merchant: formValue.merchant,
        description: formValue.description,
        category: formValue.category,
        date: formValue.date.toISOString(),
        currency: formValue.currency,
        source: 'manual'
      }).subscribe({
        next: () => {
          this.dialogRef.close(true);
        },
        error: () => {
          this.loading = false;
          this.submitting = false;
        }
      });
    }
  }

  onCancel(): void {
    this.dialogRef.close();
  }
}

