import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { backendUrl } from '../../environments';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private readonly baseUrl: string = backendUrl.apiUrl;

  constructor(private readonly http: HttpClient) {}

  getPostsForUniversity(University: string): Observable<any> {
    return this.http.get(`${this.baseUrl}/posts?`);
  }
}
