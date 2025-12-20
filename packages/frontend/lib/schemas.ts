import { z } from 'zod';

export const loginSchema = z.object({
  username: z
    .string()
    .min(1, 'Username is required')
    .regex(
      /^\\[^\\]+\\[^\\]+$/,
      'Username must be in \\domain\\username format'
    ),
  password: z.string().min(1, 'Password is required'),
});

export type LoginFormData = z.infer<typeof loginSchema>;
