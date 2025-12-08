export interface PostModel {
  id: number,
  user: number,
  user_details?: {
    id: number;
    name: string;
    email: string;
    study_program: string;
  },
  text: string,
  image: string,
  thumbnail: string,
  title: string,
  created_at: string,
  comment_count?: number
}
