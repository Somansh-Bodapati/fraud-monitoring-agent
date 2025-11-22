import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-layout',
  templateUrl: './layout.component.html',
  styleUrls: ['./layout.component.scss']
})
export class LayoutComponent {
  currentUser$;

  constructor(
    private authService: AuthService,
    private router: Router
  ) {
    this.currentUser$ = this.authService.currentUser$;
  }

  logout(): void {
    this.authService.logout();
  }

  isActive(path: string): boolean {
    return this.router.url === path || this.router.url.startsWith(path + '/');
  }
}

