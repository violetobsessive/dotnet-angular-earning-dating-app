import { inject, Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { User } from '../../Interfaces/user';
import { tap } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class AccountService {
  private http = inject(HttpClient);
  // when browser refresh, everything reset to initial value (null)
  currentUser = signal<User | null>(null);

  baseUrl = environment.apiUrl;

  login(creds: any) {
    return this.http.post<User>(this.baseUrl + 'account/login', creds).pipe(
      tap((user) => {
        if (user) {
          // key-value pair stores in browser cache
          localStorage.setItem('user', JSON.stringify(user));
          // Set user (what we get back from the API) to the currentUser signal
          this.currentUser.set(user);
        }
      }),
    );
  }
  logout() {
    localStorage.removeItem('user');
    this.currentUser.set(null);
  }
}
