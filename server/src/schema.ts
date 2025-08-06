
import { z } from 'zod';

// User schema
export const userSchema = z.object({
  id: z.number(),
  username: z.string(),
  password_hash: z.string(),
  created_at: z.coerce.date()
});

export type User = z.infer<typeof userSchema>;

// Login input schema
export const loginInputSchema = z.object({
  username: z.string().min(1, "Username is required"),
  password: z.string().min(1, "Password is required")
});

export type LoginInput = z.infer<typeof loginInputSchema>;

// Login response schema
export const loginResponseSchema = z.object({
  success: z.boolean(),
  message: z.string(),
  user: z.object({
    id: z.number(),
    username: z.string()
  }).optional()
});

export type LoginResponse = z.infer<typeof loginResponseSchema>;

// User creation input schema (for internal use)
export const createUserInputSchema = z.object({
  username: z.string().min(1, "Username is required"),
  password: z.string().min(6, "Password must be at least 6 characters")
});

export type CreateUserInput = z.infer<typeof createUserInputSchema>;
