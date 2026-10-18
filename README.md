# mrpack-audit

Audit a Modrinth modpack or mods folder for licence and provenance risk before you publish it.

Built for packs like Outbreak Zone: it answers "is everything in this pack actually allowed to be redistributed?" before a Modrinth reviewer or an angry mod author answers it for you.

## What it does

- Hashes every `.jar` and `.zip` in a folder, or every file inside a `.mrpack` (both the `modrinth.index.json` entries and anything bundled in `overrides/`).
- Matches each hash against the Modrinth API to find the real project behind the file.
- Pulls each project's licence and classifies it: permissive, copyleft, restricted (all rights reserved / custom), or unknown.
- Flags files that are not on Modrinth at all, so unprovenanced downloads cannot slip through.

## Install

```
pip install .
```

Requires Python 3.10+. No dependencies.

## Usage

```
mrpack-audit path/to/pack.mrpack
mrpack-audit path/to/mods/
mrpack-audit pack.mrpack --json      # machine readable output
mrpack-audit pack.mrpack --strict    # exit 1 if anything needs attention (CI friendly)
```

Example output:

```
FILE        PROJECT         LICENSE  STATUS
--------    -------------   -------  ------
good.jar    Better Zombies  MIT      ok
bad.zip     Tissou Pack     ARR      FLAG
stray.jar   -               -        check

Summary: 1 permissive, 1 restricted, 1 unmatched

Needs attention:
  bad.zip: Tissou Pack is ARR, do not redistribute without permission
  stray.jar: not found on Modrinth, provenance unverified
```

## Licence classes

- **permissive** (MIT, Apache, BSD, CC0, ...): fine to bundle, keep the credit line.
- **copyleft** (GPL, LGPL, MPL, ...): generally fine for unmodified jars, read the licence if you modify.
- **restricted** (all rights reserved, custom LicenseRef): do not redistribute without written permission from the author.
- **unknown** / **unmatched**: check by hand before shipping.

## Licence

MIT
