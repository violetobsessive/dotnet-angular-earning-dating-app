import { HttpClient } from '@angular/common/http';
import { Component, inject, OnInit, signal } from '@angular/core';
import { lastValueFrom } from 'rxjs';
import { AccountService } from '../core/services/account-service';
import { Nav } from '../layout/nav/nav';

@Component({
  selector: 'app-root',
  imports: [Nav],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App implements OnInit {
  private accountService = inject(AccountService);
  private http = inject(HttpClient);
  protected readonly title = 'Dating app';

  protected members = signal<any>([]);

  async ngOnInit() {
    this.members.set(await this.getMembers());
    this.setCurrentUser;
    // this.http.get('https://localhost:5001/api/members').subscribe({
    // next: (response) => this.members.set(response),
    // error: (error) => console.log(error),
    // complete: () => console.log('Completed the http request'),
    //});
  }

  setCurrentUser() {
    const userString = localStorage.getItem('user');
    if (!userString) return;
    const user = JSON.parse(userString);
    this.accountService.currentUser.set(user);
  }

  async getMembers() {
    try {
      return lastValueFrom(this.http.get('https://localhost:5001/api/members'));
    } catch (error) {
      console.log(error);
      throw error;
    }
  }
}
