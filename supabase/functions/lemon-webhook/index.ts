// Supabase Edge Function: receives Lemon Squeezy webhooks and sets profiles.plan.
// Deploy with: supabase functions deploy lemon-webhook --no-verify-jwt   (see README.md)
import { handleRequest } from "./handler.ts";

Deno.serve((req: Request) => handleRequest(req, Deno.env.toObject(), fetch));
