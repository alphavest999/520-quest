# Lemon Squeezy webhook

Receives Lemon Squeezy subscription events and sets `profiles.plan` through `public.apply_payment()` (see `supabase/002_payments.sql`). Nothing in the app can change a plan any other way.

## How a purchase flows

1. Signed-in user taps **Choose** in the app. The checkout link carries their account id and email.
2. Lemon Squeezy takes the payment and calls this function with an `X-Signature` header. The function checks the signature, works out the plan from the variant id and calls the database.
3. The database sets the plan. If nobody has that email yet, the plan waits in `pending_plans` and is applied the moment that account is created.
4. The app (signed in) polls the profile for up to 90 seconds after checkout and unlocks.

Handled events: `subscription_created`, `_updated`, `_resumed`, `_unpaused`, `_cancelled`, `_paused`, `_expired`. A cancelled subscription keeps access until its `ends_at`; expired, paused and unpaid revoke it. Refunds (`order_refunded`) are not handled: after a refund, set the plan by hand in the table editor.

## One-time setup (test mode)

1. **Database:** run `supabase/002_payments.sql` in the Supabase SQL Editor.
2. **Lemon Squeezy:** turn on **Test mode** (top of the dashboard). Create three subscription products (Monthly $14.99, 6 Months $44.99, Yearly $59.99). For each, note the **product id** (Products list, the product's ⋯ menu) and copy the **checkout link** (Share).
3. **Deploy the function.** Without the CLI: Supabase > Edge Functions > Deploy a new function > Via Editor, name it `lemon-webhook`, paste all of `single-file.ts` (built by `node bundle.mjs`), deploy, then turn **Verify JWT** off in the function's settings and add the secrets below under Edge Functions > Secrets. With the CLI:
   ```
   supabase functions deploy lemon-webhook --no-verify-jwt
   supabase secrets set LS_WEBHOOK_SECRET=<a long random string you choose> \
     LS_PRODUCT_MONTHLY=<id> LS_PRODUCT_SIXMONTH=<id> LS_PRODUCT_YEARLY=<id> LS_MODE=test
   ```
   `LS_VARIANT_MONTHLY` / `_SIXMONTH` / `_YEARLY` work too, if you prefer variant ids. If an id is wrong, the delivery's response in Lemon Squeezy's webhook log says `unknown product <id>`, which tells you the right one.
   Turning JWT verification off is required: Lemon Squeezy has no Supabase login, and the signature check is what protects the endpoint. `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are provided automatically.
4. **Webhook:** Lemon Squeezy > Settings > Webhooks > add `https://<project-ref>.supabase.co/functions/v1/lemon-webhook`, signing secret = the same `LS_WEBHOOK_SECRET`, and tick the seven subscription events above.
5. **App:** in `play/index.html` paste the three test-mode checkout links into `testUrl` of `CONFIG.plans`. They are used only on `localhost` (or after opening the app once with `?paytest=1`), so real visitors never see them.

## Test without a real charge

Open `http://localhost:8000/play/index.html`, sign in, open **See plans**, choose a plan and pay with:

- Card `4242 4242 4242 4242`, any future expiry, any CVC.

Then check `select email, plan, plan_since from profiles` and `select * from payment_events order by received_at desc` in Supabase. The plan should appear within seconds. Lemon Squeezy's webhook page also lists every delivery with its response.

## Going live

1. Create the same three products in live mode, put their checkout links in `url` of `CONFIG.plans` and in `config.js`.
2. Add a second webhook in live mode (same URL, same signing secret: you choose the secret yourself) and update the three `LS_PRODUCT_*` ids to the live products, which differ from the test ones.
3. `supabase secrets set LS_MODE=live`. In `live` mode test events are ignored; in `test` mode live events are ignored; `both` accepts either.

## Run the tests locally

```
node --test supabase/functions/lemon-webhook/logic.test.ts
```

Needs Node 22.18 or newer. Covers the signature check, every plan decision and the request handler with a fake database.
