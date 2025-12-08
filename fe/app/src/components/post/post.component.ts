import {Component, Input, OnInit} from '@angular/core';
import {PostModel} from '../../app/models/post.model';
import {CommentModel} from '../../app/models/comment.model';
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
import {MatFormField, MatLabel} from '@angular/material/form-field';
import {MatInput} from '@angular/material/input';
import {FormsModule} from '@angular/forms';
import {NgForOf, NgIf} from '@angular/common';
import {environment} from '../../environments';
import {ApiService} from '../../app/services/api.service';

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
    MatIconButton,
    MatFormField,
    MatInput,
    MatLabel,
    FormsModule,
    NgIf,
    NgForOf
  ],
  templateUrl: './post.component.html',
  styleUrl: './post.component.css',
})
export class PostComponent implements OnInit{
  @Input() post!: PostModel; // Empfängt die Post-Daten
  formattedDate: string = '';
  comments: CommentModel[] = [];
  showComments: boolean = false;
  showCommentInput: boolean = false;
  newCommentText: string = '';

  constructor(private apiService: ApiService) {}

  ngOnInit(): void {
    if (this.post && this.post.created_at) {
      this.formattedDate = new Date(this.post.created_at).toLocaleDateString('de-DE', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    }
  }

  onLike(): void {
    console.log(`Post ${this.post.id} geliked!`);
  }

  toggleComments(): void {
    this.showComments = !this.showComments;
    if (this.showComments && this.comments.length === 0) {
      this.loadComments();
    }
  }

  loadComments(): void {
    this.apiService.getCommentsForPost(this.post.id).subscribe({
      next: (comments) => {
        // Sort comments by created_at in descending order (newest first)
        this.comments = comments.sort((a, b) => 
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        );
      },
      error: (error) => {
        console.error('Fehler beim Laden der Kommentare:', error);
      }
    });
  }

  toggleCommentInput(): void {
    this.showCommentInput = !this.showCommentInput;
  }

  submitComment(): void {
    if (!this.newCommentText.trim()) {
      return;
    }

    const comment = {
      user: this.post.user, // Using the post's user as the commenter
      post: this.post.id,
      text: this.newCommentText
    };

    this.apiService.createComment(comment).subscribe({
      next: (createdComment) => {
        // Add the new comment to the beginning of the array
        this.comments.unshift(createdComment);
        this.newCommentText = '';
        this.showCommentInput = false;
        this.showComments = true;
      },
      error: (error) => {
        console.error('Fehler beim Erstellen des Kommentars:', error);
      }
    });
  }

  formatCommentDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString('de-DE', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  protected readonly environment = environment;
}
