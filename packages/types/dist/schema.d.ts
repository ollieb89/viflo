import { z } from 'zod';
export declare const UserSchema: z.ZodObject<{
    id: z.ZodString;
    email: z.ZodString;
}, "strip", z.ZodTypeAny, {
    id: string;
    email: string;
}, {
    id: string;
    email: string;
}>;
export type User = z.infer<typeof UserSchema>;
//# sourceMappingURL=schema.d.ts.map