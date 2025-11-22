import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { HttpClientModule, HTTP_INTERCEPTORS } from '@angular/common/http';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { LoginComponent } from './components/login/login.component';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { TransactionsComponent } from './components/transactions/transactions.component';
import { AlertsComponent } from './components/alerts/alerts.component';
import { ReportsComponent } from './components/reports/reports.component';
import { LayoutComponent } from './components/layout/layout.component';
import { AddTransactionModalComponent } from './components/add-transaction-modal/add-transaction-modal.component';

import { AuthInterceptor } from './interceptors/auth.interceptor';
import { AuthService } from './services/auth.service';
import { TransactionService } from './services/transaction.service';
import { AlertService } from './services/alert.service';
import { DashboardService } from './services/dashboard.service';

import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatDialogModule } from '@angular/material/dialog';
import { MatTableModule } from '@angular/material/table';
import { MatChipsModule } from '@angular/material/chips';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatSelectModule } from '@angular/material/select';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

@NgModule({
  declarations: [
    AppComponent,
    LoginComponent,
    DashboardComponent,
    TransactionsComponent,
    AlertsComponent,
    ReportsComponent,
    LayoutComponent,
    AddTransactionModalComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    BrowserAnimationsModule,
    HttpClientModule,
    ReactiveFormsModule,
    FormsModule,
    MatToolbarModule,
    MatButtonModule,
    MatCardModule,
    MatInputModule,
    MatFormFieldModule,
    MatIconModule,
    MatDialogModule,
    MatTableModule,
    MatChipsModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatNativeDateModule,
    MatSelectModule,
    MatProgressSpinnerModule
  ],
  providers: [
    AuthService,
    TransactionService,
    AlertService,
    DashboardService,
    {
      provide: HTTP_INTERCEPTORS,
      useClass: AuthInterceptor,
      multi: true
    }
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }

