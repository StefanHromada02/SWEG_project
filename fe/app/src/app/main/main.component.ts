import {Component, inject, OnInit} from '@angular/core';
import {ApiService} from '../services/api.service';
import {PostComponent} from '../../components/post/post.component';
import {Observable} from 'rxjs';
import {AsyncPipe, CommonModule} from '@angular/common';
import {NewPostModal} from '../../components/new-post-modal/new-post-modal';
import {KeycloakService} from 'keycloak-angular';
import {MatButtonModule} from '@angular/material/button';
import {MatIconModule} from '@angular/material/icon';

@Component({
  selector: 'app-main',
  imports: [
    CommonModule,
    PostComponent,
    AsyncPipe,
    NewPostModal,
    MatButtonModule,
    MatIconModule,
  ],
  templateUrl: './main.component.html',
  styleUrl: './main.component.css',
})
export class MainComponent implements OnInit {
  apiService = inject(ApiService);
  keycloak = inject(KeycloakService);
  posts$!: Observable<any[]>;
  isLoggedIn = false;
  username = '';

  async ngOnInit() {
    this.refreshPosts();
    
    // Check if user is logged in
    this.isLoggedIn = await this.keycloak.isLoggedIn();
    if (this.isLoggedIn) {
      const userProfile = await this.keycloak.loadUserProfile();
      this.username = userProfile.username || userProfile.email || 'User';
    }
  }

  onCreated() {
    this.refreshPosts();
  }

  login() {
    this.keycloak.login();
  }

  logout() {
    this.keycloak.logout();
  }

  private refreshPosts() {
    this.posts$ = this.apiService.getPostsForUniversity("Technikum");
  }
}
