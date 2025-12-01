import {Component, Input, OnInit} from '@angular/core';
import {PostModel} from '../../app/models/post.model';
import {
  MatCard,
  MatCardActions,
  MatCardContent,
  MatCardHeader,
  MatCardSubtitle,
  MatCardTitle
} from '@angular/material/card';
import {MatIcon} from '@angular/material/icon';
import {MatButton, MatIconButton} from '@angular/material/button';
import {environment} from '../../environments';

@Component({
  selector: 'app-post',
  imports: [
    MatCardContent,
    MatCardActions,
    MatCard,
    MatCardHeader,
    MatCardTitle,
    MatCardSubtitle,
    MatIcon,
    MatButton,
    MatIconButton
  ],
  templateUrl: './post.component.html',
  styleUrl: './post.component.css',
})
export class PostComponent implements OnInit{
  @Input() post!: PostModel; // Empfängt die Post-Daten
  formattedDate: string = '';

  ngOnInit(): void {
    if (this.post && this.post.createdAt) {
      this.formattedDate = new Date(this.post.createdAt).toLocaleDateString('de-DE', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    }
  }

  onLike(): void {
    console.log(`Post ${this.post.id} geliked!`);
  }

  protected readonly environment = environment;
}
