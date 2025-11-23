import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface Transaction {
  id: number;
  userId: number;
  amount: number;
  currency: string;
  date: string;
  description?: string;
  merchant?: string;
  category?: string;
  subcategory?: string;
  status: string;
  isAnomaly: boolean;
  anomalyScore?: number;
  riskScore?: number;
  isReconciled: boolean;
}

export interface TransactionCreateRequest {
  amount: number;
  currency?: string;
  date: string;
  description?: string;
  merchant?: string;
  category?: string;
  source?: string;
  receiptId?: number;
}

@Injectable({
  providedIn: 'root'
})
export class TransactionService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) { }

  getTransactions(page: number = 0, size: number = 100): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/transactions?page=${page}&size=${size}`);
  }

  getTransaction(id: number): Observable<Transaction> {
    return this.http.get<Transaction>(`${this.apiUrl}/transactions/${id}`);
  }

  createTransaction(transaction: TransactionCreateRequest): Observable<Transaction> {
    return this.http.post<Transaction>(`${this.apiUrl}/transactions`, transaction);
  }

  updateTransactionStatus(id: number, status: string): Observable<Transaction> {
    return this.http.patch<Transaction>(`${this.apiUrl}/transactions/${id}/status`, { status });
  }

  deleteTransaction(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/transactions/${id}`);
  }

  getEntitlements(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/entitlements/actions`);
  }
}

