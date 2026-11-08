# Lemon Squeezy product images

All images are 1652 x 1240 (4:3), the size Lemon Squeezy recommends. Lemon Squeezy shows a product's
images on its checkout page, in emails and on the dashboard, so these double as the checkout images.

| Product | Image 1 (main + checkout) | Images 2, 3, 4 (same for every plan) |
|---|---|---|
| Monthly $14.99 | plan-monthly.png | feature-1-explanations.png, feature-2-plan.png, feature-3-course.png |
| 6 Months $44.99 | plan-6-months.png | same three |
| Yearly $59.99 | plan-yearly.png | same three |

## How to upload (do this once per product)

1. Go to app.lemonsqueezy.com and click **Products** on the left.
2. Click the product name (for example "Monthly").
3. Scroll to the **Media** box and drag the four images in, or click it to pick them.
4. Make sure the plan image (plan-....png) is **first**. Drag it to the front if it isn't. The first image is the one people see at checkout.
5. Click **Update product** (or **Save**) at the bottom.
6. Open the product's checkout link to check it looks right.

Repeat for the other two products. If you later make live-mode copies of the products, upload the same images there too.

To rebuild after a price or wording change: edit `tools/lemonsqueezy/render.js`, then run
`node tools/lemonsqueezy/render.js` from the repo root.
