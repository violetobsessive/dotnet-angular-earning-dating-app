import { inject, Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root',
})
export class AccountService {
  private http = inject(HttpClient);
  currentUser = signal<any>(null);

  baseUrl = environment.apiUrl;

  login(creds: any) {
    return this.http.post(this.baseUrl + 'account/login', creds);
  }
}
