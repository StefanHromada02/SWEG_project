import {Component, Input} from '@angular/core';
import {PostModel} from '../../app/models/post.model';

@Component({
  selector: 'app-post',
  imports: [],
  templateUrl: './post.component.html',
  styleUrl: './post.component.css',
})
export class PostComponent{
  @Input() post?: PostModel;
}
