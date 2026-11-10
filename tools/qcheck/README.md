# Question bank check

`check_bank.js` reads every question in `play/bank` (the free files and, with the content key, the sealed paid
files) plus the older questions inside `play/index.html`, and runs on every pull request through
`.github/workflows/qcheck.yml`. A red check means the PR should not merge yet.

## What fails a PR

- An answer key that isn't A-D, or a question without exactly 4 non-empty choices.
- Two right answers or a wrong key: a wrong choice explained as "Correct", a key not explained as "Correct",
  or a full explanation (`ex/`) that disagrees with the key.
- Duplicate choices, a missing or stub explanation, a choice with no reason.
- A passage question that points at a Table, Figure or paragraph the passage doesn't have.
- A free copy (BP.json, CARS.json, FL.json, MN.json) whose key, stem or choices differ from its sealed twin.
- Duplicate question ids.
- A new giveaway: the key is the only choice with (or without) a unit, uses a unit no other choice uses, or is
  much longer or shorter than every other choice. Giveaways that already existed are listed in
  `baseline.json` and don't fail.
- A section where new questions push "the key is the longest choice" further from 25% than the baseline.

## Running it

    node tools/qcheck/check_bank.js                                          # free files only
    CONTENT_KEY_FILE=<path to content.key> node tools/qcheck/check_bank.js   # also the sealed files

The workflow reads the key from the repository secret `CONTENT_KEY` (the one line in content.key). Without
it, the check still runs on the free files and says the sealed files were skipped.

If a flagged giveaway is fine on purpose, accept it with `--update-baseline` (needs the key) and commit
`baseline.json` in the same PR.
