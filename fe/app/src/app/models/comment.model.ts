export interface CommentModel {
  id: number;
  user: number;
  user_details?: {
    id: number;
    name: string;
    email: string;
  };
  post: number;
  text: string;
  created_at: string;
}
