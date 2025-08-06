
import { initTRPC } from '@trpc/server';
import { createHTTPServer } from '@trpc/server/adapters/standalone';
import 'dotenv/config';
import cors from 'cors';
import superjson from 'superjson';
import { z } from 'zod';

import { loginInputSchema, createUserInputSchema } from './schema';
import { login } from './handlers/login';
import { getUser } from './handlers/get_user';
import { createUser } from './handlers/create_user';

const t = initTRPC.create({
  transformer: superjson,
});

const publicProcedure = t.procedure;
const router = t.router;

const appRouter = router({
  healthcheck: publicProcedure.query(() => {
    return { status: 'ok', timestamp: new Date().toISOString() };
  }),
  
  login: publicProcedure
    .input(loginInputSchema)
    .mutation(({ input }) => login(input)),
    
  getUser: publicProcedure
    .input(z.object({ userId: z.number() }))
    .query(({ input }) => getUser(input.userId)),
    
  createUser: publicProcedure
    .input(createUserInputSchema)
    .mutation(({ input }) => createUser(input)),
});

export type AppRouter = typeof appRouter;

async function start() {
  const port = process.env['SERVER_PORT'] || 2022;
  const server = createHTTPServer({
    middleware: (req, res, next) => {
      cors()(req, res, next);
    },
    router: appRouter,
    createContext() {
      return {};
    },
  });
  server.listen(port);
  console.log(`TRPC server listening at port: ${port}`);
  console.log(`Demo user credentials: username="demo", password="demo123"`);
}

start();
